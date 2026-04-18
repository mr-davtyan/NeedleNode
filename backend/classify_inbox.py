import os
import shutil
import argparse
import io
import tempfile
import warnings
import pyembroidery
from PIL import Image
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from backend.state import import_state
from backend.database import SessionLocal, Tag, file_tag
from sqlalchemy import func

# Ensure we are running from project root
INBOX_DIR = "inbox"
LIBRARY_DIR = "library"

class SkipLargeImageError(Exception):
    pass

SUPPORTED_EXTENSIONS = (".pes", ".dst", ".jef", ".exp", ".vp3", ".hus", ".pec", ".vip", ".shv", ".sew")

# Validate API Key
if not os.environ.get("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY environment variable not set. Script may fail.")

class FileClassification(BaseModel):
    filename: str = Field(description="The exact filename of the image being classified. Used to match classification back to the file.")
    main_tag: str = Field(description="The single most descriptive primary category (e.g., Animals, Floral, Christmas). Capitalize first letter.")
    sub_tags: list[str] = Field(description="List of 3-5 descriptive tags (e.g., ['dog', 'outline']). All lowercase.")
    main_colors: list[str] = Field(description="List of up to 4 dominant colors (e.g., ['red', 'gold']). All lowercase.")

class BatchClassification(BaseModel):
    results: list[FileClassification]

def render_embroidery_to_image(emb_path: str) -> Image.Image:
    """
    Renders an embroidery file to a PIL Image using pyembroidery.
    """
    # Temporary file for pyembroidery to write to
    temp_png = os.path.join(tempfile.gettempdir(), f".temp_{os.path.basename(emb_path)}.png")
    try:
        pattern = pyembroidery.read(emb_path)
        if not pattern:
            raise ValueError(f"Could not read pattern from {emb_path}")
            
        pyembroidery.write_png(pattern, temp_png)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            try:
                img = Image.open(temp_png).convert("RGBA")
            except (Image.DecompressionBombError, Image.DecompressionBombWarning):
                raise SkipLargeImageError(f"Image too large: {os.path.basename(emb_path)}")
                
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, (0, 0), img) # Paste with mask
        img = background
        img.thumbnail((256, 256))
        return img
    except SkipLargeImageError:
        raise
    except Exception as e:
        raise SkipLargeImageError(f"Rendering error for {os.path.basename(emb_path)}: {e}")
    finally:
        if os.path.exists(temp_png):
            os.remove(temp_png)

def classify_embroidery_batch(client: genai.Client, images_with_filenames: list[tuple[Image.Image, str, str]], existing_main_tags: list[str] = []) -> list[FileClassification]:
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

    existing_list_str = ", ".join([f"'{t}'" for t in existing_main_tags[:50]]) if existing_main_tags else "None"
    
    prompt = f"""
    You are an expert at organizing embroidery designs.
    Analyze the attached embroidery pattern images.
    
    CRITICAL: There are EXACTLY {len(images_with_filenames)} images attached. You MUST return a classification for EVERY SINGLE ONE of them. 
    The file order is: {", ".join(filenames_list)}.
    
    For each image:
    1. Identify the **Main Tag** (Primary Category).
       - ALWAYS use the **Singular** form where applicable (e.g., use 'Frame' instead of 'Frames', 'Fairy' instead of 'Fairies', 'Flower' instead of 'Flowers').
       - **Existing Categories**: {existing_list_str}
       - **Rule**: If the image fits well into ONE of the Existing Categories listed above, REUSE THAT CATEGORY EXACTLY to avoid duplicates. Otherwise, create a new singular category.
    2. Identify **Sub-tags** (Descriptive keywords).
    3. Identify **Main Colors** (Up to 4 dominant colors).
    
    Return a structured JSON match containing a list of classification results. Verify that the length of the results list is {len(images_with_filenames)}.
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

def get_unique_target_path(target_dir: str, main_tag: str, sub_tags_str: str, orig_name_clean: str, orig_ext: str) -> tuple[str, str]:
    """
    Constructs a unique target path by appending _1, _2, etc. if needed.
    """
    base_new = f"{main_tag}"
    if sub_tags_str:
        base_new += f" ({sub_tags_str})"
    base_new += f" {orig_name_clean}"
    
    new_filename = f"{base_new}{orig_ext}"
    target_path = os.path.join(target_dir, new_filename)
    
    counter = 1
    while os.path.exists(target_path):
        new_filename = f"{base_new}_{counter}{orig_ext}"
        target_path = os.path.join(target_dir, new_filename)
        counter += 1
         
    return target_path, new_filename

def process_inbox(dry_run=True, limit=None, batch_size=6):
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
        # 0. Get existing main tags for prompt context to avoid singular/plural conflicts
        existing_main_tags = []
        if os.path.exists(LIBRARY_DIR):
             # Always include ALL main category folders (prevents duplicate category creation)
             existing_main_tags = [
                 d for d in os.listdir(LIBRARY_DIR)
                 if os.path.isdir(os.path.join(LIBRARY_DIR, d))
             ]
             
             # If under 50, pad with the most popular sub-tags from the DB
             if len(existing_main_tags) < 50:
                 needed = 50 - len(existing_main_tags)
                 main_tags_set = set(t.lower() for t in existing_main_tags)
                 db = SessionLocal()
                 try:
                     popular_subtags = (
                         db.query(Tag.name, func.count(file_tag.c.file_id).label("cnt"))
                         .join(file_tag, Tag.id == file_tag.c.tag_id)
                         .filter(Tag.is_main == False)
                         .group_by(Tag.id)
                         .order_by(func.count(file_tag.c.file_id).desc())
                         .limit(needed * 2)  # overfetch to allow dedup
                         .all()
                     )
                     for tag_name, _ in popular_subtags:
                         if tag_name.lower() not in main_tags_set and len(existing_main_tags) < 50:
                             existing_main_tags.append(tag_name)
                 finally:
                     db.close()
             
        # 1. Collect all files first to facilitate batching
        all_files = []
        for root, dirs, files in os.walk(INBOX_DIR):
             for file in files:
                 if file.lower().endswith(SUPPORTED_EXTENSIONS):
                     pes_path = os.path.join(root, file)
                     rel_path = os.path.relpath(pes_path, INBOX_DIR)
                     all_files.append((pes_path, file, rel_path))

        if not all_files:
            print("No supported embroidery files found in inbox.")
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
            
            for pes_path, file, rel_path in current_batch_files:
                import_state.current_file = file
                try:
                    img = render_embroidery_to_image(pes_path)
                    batch_images.append((img, rel_path, pes_path))
                    valid_files_in_batch.append((pes_path, file, rel_path))
                except SkipLargeImageError as e:
                    print(f"  {e}")
                    SKIPPED_DIR = "trash/SKIPPED"
                    os.makedirs(SKIPPED_DIR, exist_ok=True)
                    shutil.move(pes_path, os.path.join(SKIPPED_DIR, os.path.basename(pes_path)))
                    fail_count += 1
                    # Progress still counts as "processed" for UI
                    import_state.processed += 1
                except Exception as e:
                    print(f"  Error rendering {file}: {e}")
                    fail_count += 1
                    import_state.processed += 1

            if not batch_images:
                continue

            try:
                results = classify_embroidery_batch(client, batch_images, existing_main_tags=existing_main_tags)
                results_dict = {r.filename: r for r in results}
                
                for pes_path, file, rel_path in valid_files_in_batch:
                    if import_state.stop_requested:
                         break
                         
                    classification = results_dict.get(rel_path)
                    if not classification:
                        print(f"  Warning: No classification returned for {file}")
                        print(f"  Gemini returned: {[r.filename for r in results]}")
                        fail_count += 1
                        import_state.processed += 1
                        continue

                    main_tag = classification.main_tag.strip().replace(" ", "_").replace("/", "-")
                    sub_tags = [t.strip().replace(" ", "-").replace("/", "-") for t in classification.sub_tags]
                    main_colors = [c.strip().replace(" ", "-").replace("/", "-") for c in classification.main_colors] if hasattr(classification, "main_colors") else []
                    
                    if not main_tag:
                        main_tag = "Unsorted"
                        
                    print(f"\nFile: {file}")
                    print(f"  > Main Tag: {main_tag}")
                    print(f"  > Sub Tags: {sub_tags}")
                    print(f"  > Colors: {main_colors}")
                    
                    combined_tags = list(dict.fromkeys(sub_tags + main_colors))
                    sub_tags_str = ",".join(combined_tags)
                    orig_name_clean = os.path.splitext(file)[0]
                    orig_ext = os.path.splitext(file)[1]
                    
                    target_dir = os.path.join(LIBRARY_DIR, main_tag)
                    target_path, new_filename = get_unique_target_path(target_dir, main_tag, sub_tags_str, orig_name_clean, orig_ext)
                    
                    print(f"  > Target: {target_path}")
                    
                    # Log rename for collisions
                    initial_filename = f"{main_tag}"
                    if sub_tags_str:
                         initial_filename += f" ({sub_tags_str})"
                    initial_filename += f" {orig_name_clean}{orig_ext}"
                    
                    if new_filename != initial_filename:
                         print(f"  -> Renamed to avoid collision: {new_filename}")
                    
                    if not dry_run:
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.move(pes_path, target_path)
                        print("  [MOVED]")
                    
                    success_count += 1
                    import_state.processed += 1

            except Exception as e:
                print(f"Batch processing failed: {e}")
                batch_len = len(current_batch_files)
                fail_count += batch_len
                import_state.processed += batch_len
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
    parser.add_argument("--batch-size", type=int, default=6, help="Number of files to process per Gemini call")
    parser.add_argument("--api-key", type=str, help="Gemini API Key")
    args = parser.parse_args()

    if args.api_key:
        os.environ["GEMINI_API_KEY"] = args.api_key

    is_dry = args.dry_run or (not args.run)
    process_inbox(dry_run=is_dry, limit=args.limit, batch_size=args.batch_size)
