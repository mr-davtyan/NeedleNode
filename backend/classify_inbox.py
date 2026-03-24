import os
import shutil
import argparse
import io
import pyembroidery
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from backend.state import import_state

# Ensure we are running from project root
INBOX_DIR = "inbox"
LIBRARY_DIR = "library"

# Validate API Key
if not os.environ.get("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY environment variable not set. Script may fail.")

class FileClassification(BaseModel):
    filename: str = Field(description="The exact filename of the image being classified. Used to match classification back to the file.")
    main_tag: str = Field(description="The single most descriptive primary category (e.g., Animals, Floral, Christmas). Capitalize first letter.")
    sub_tags: list[str] = Field(description="List of 3-5 descriptive tags (e.g., ['dog', 'outline']). All lowercase.")

class BatchClassification(BaseModel):
    results: list[FileClassification]

def render_pes_to_image(pes_path: str) -> Image.Image:
    """
    Renders a .pes file to a PIL Image using pyembroidery.
    """
    pattern = pyembroidery.read(pes_path)
    if not pattern:
        raise ValueError(f"Could not read pattern from {pes_path}")
        
    # Temporary file for pyembroidery to write to
    temp_png = f".temp_{os.path.basename(pes_path)}.png"
    try:
        pyembroidery.write_png(pattern, temp_png)
        img = Image.open(temp_png).convert("RGBA")
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, (0, 0), img) # Paste with mask
        img = background
        img.thumbnail((1024, 1024))
        return img
    finally:
        if os.path.exists(temp_png):
            os.remove(temp_png)

def classify_embroidery_batch(client: genai.Client, images_with_filenames: list[tuple[Image.Image, str, str]]) -> list[FileClassification]:
    """
    Sends a batch of images to Gemini for classification with structured output.
    """
    contents = []
    filenames_list = []
    
    for idx, (img, name, _) in enumerate(images_with_filenames):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        contents.append(types.Part.from_bytes(
            data=img_bytes,
            mime_type='image/png',
        ))
        filenames_list.append(name)

    prompt = f"""
    You are an expert at organizing embroidery designs.
    Analyze the attached embroidery pattern images.
    
    There are {len(images_with_filenames)} images attached, in the order of the files: {", ".join(filenames_list)}.
    Please classify EACH image. Ensure the `filename` in your response matches the exact filenames provided.
    
    For each image:
    1. Identify the **Main Tag** (Primary Category).
    2. Identify **Sub-tags** (Descriptive keywords).
    
    Return a structured JSON match containing a list of classification results.
    """
    contents.append(prompt)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BatchClassification,
            temperature=0.1,
        ),
    )
    
    try:
        batch_res = BatchClassification.model_validate_json(response.text)
        return batch_res.results
    except Exception as e:
        print(f"Failed to validate response: {e}")
        print(f"Response text: {response.text}")
        raise e

def process_inbox(dry_run=True, limit=None, batch_size=4):
    client = genai.Client() # Uses GEMINI_API_KEY
    
    if not os.path.exists(INBOX_DIR):
        print(f"Inbox directory '{INBOX_DIR}' not found.")
        return

    import_state.reset()
    import_state.is_importing = True
    
    # Counter
    success_count = 0
    fail_count = 0

    print(f"--- Starting Batch Classification ({'DRY RUN' if dry_run else 'LIVE'}) ---")
    if limit:
        print(f"Limit: {limit} files")
    print(f"Batch Size: {batch_size}")

    try:
        # 1. Collect all files first to facilitate batching
        all_files = []
        for root, dirs, files in os.walk(INBOX_DIR):
             for file in files:
                 if file.lower().endswith(".pes"):
                     all_files.append((os.path.join(root, file), file))

        if not all_files:
            print("No .pes files found in inbox.")
            return

        import_state.total = len(all_files)
        print(f"Found {len(all_files)} files total in inbox.")

        # 2. Process in batches
        for i in range(0, len(all_files), batch_size):
            if import_state.stop_requested:
                 print("\nImport stopped by user request.")
                 break
                 
            if limit and success_count >= limit:
                 print(f"\nReached limit of {limit} files. Stopping.")
                 break

            current_batch_files = all_files[i : i + batch_size]
            if limit and success_count + len(current_batch_files) > limit:
                 current_batch_files = current_batch_files[: limit - success_count]

            print(f"\n--- Processing Batch of {len(current_batch_files)} files ---")
            
            batch_images = []
            valid_files_in_batch = []
            
            for pes_path, file in current_batch_files:
                import_state.current_file = file
                try:
                    img = render_pes_to_image(pes_path)
                    batch_images.append((img, file, pes_path))
                    valid_files_in_batch.append((pes_path, file))
                except Exception as e:
                    print(f"  Error rendering {file}: {e}")
                    fail_count += 1

            if not batch_images:
                continue

            try:
                results = classify_embroidery_batch(client, batch_images)
                results_dict = {r.filename: r for r in results}
                
                for pes_path, file in valid_files_in_batch:
                    if import_state.stop_requested:
                         break
                         
                    classification = results_dict.get(file)
                    if not classification:
                        print(f"  Warning: No classification returned for {file}")
                        fail_count += 1
                        continue

                    main_tag = classification.main_tag.strip().replace(" ", "_").replace("/", "-")
                    sub_tags = [t.strip().replace(" ", "-") for t in classification.sub_tags]
                    
                    if not main_tag:
                        main_tag = "Unsorted"
                        
                    print(f"\nFile: {file}")
                    print(f"  > Main Tag: {main_tag}")
                    print(f"  > Sub Tags: {sub_tags}")
                    
                    sub_tags_str = ",".join(sub_tags)
                    orig_name_clean = os.path.splitext(file)[0]
                    
                    new_filename = f"{main_tag}"
                    if sub_tags_str:
                         new_filename += f" ({sub_tags_str})"
                    new_filename += f" {orig_name_clean}.pes"
                    
                    target_dir = os.path.join(LIBRARY_DIR, main_tag)
                    target_path = os.path.join(target_dir, new_filename)
                    
                    print(f"  > Target: {target_path}")
                    
                    if not dry_run:
                        os.makedirs(target_dir, exist_ok=True)
                        if os.path.exists(target_path):
                             print(f"  ! File already exists at target: {target_path}. Skipping.")
                             fail_count += 1
                             continue
                             
                        shutil.move(pes_path, target_path)
                        print("  [MOVED]")
                    
                    success_count += 1
                    import_state.processed = success_count

            except Exception as e:
                print(f"Batch processing failed: {e}")
                fail_count += len(current_batch_files)
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("Quota exceeded or rate limited. Aborting further requests.")
                    break

    finally:
        # Cleanup empty subdirectories in inbox
        if not dry_run and os.path.exists(INBOX_DIR):
            for root, dirs, files in os.walk(INBOX_DIR, topdown=False):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        if not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except Exception:
                        pass
                        
        import_state.is_importing = False
        print(f"\n--- Summary ---")
        print(f"Processed: {success_count}")
        print(f"Failed:    {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify embroidery files from inbox to library with AI.")
    parser.add_argument("--run", action="store_true", help="Perform actual file moving (defaults to dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (default)")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    parser.add_argument("--batch-size", type=int, default=4, help="Number of files to process per Gemini call")
    parser.add_argument("--api-key", type=str, help="Gemini API Key")
    args = parser.parse_args()

    if args.api_key:
        os.environ["GEMINI_API_KEY"] = args.api_key

    is_dry = args.dry_run or (not args.run)
    process_inbox(dry_run=is_dry, limit=args.limit, batch_size=args.batch_size)
