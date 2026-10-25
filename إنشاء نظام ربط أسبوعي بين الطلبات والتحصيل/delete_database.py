import os
import glob
import shutil

def delete_database_files():
    print("=======================================================")
    print("   Deleting Database, Reports, and Samples Files       ")
    print("=======================================================")

    patterns = ["*.db", "*.sqlite", "*.sqlite3"]
    files_deleted = 0

    for pattern in patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"[SUCCESS] Deleted Database: {file_path}")
                files_deleted += 1
            except Exception as e:
                print(f"[ERROR] Failed to delete {file_path}: {e}")

    # Delete reports and samples folders
    folders_to_delete = ["reports", "samples", "data"]
    folders_deleted = 0
    
    for folder in folders_to_delete:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"[SUCCESS] Deleted folder: {folder}")
                folders_deleted += 1
            except Exception as e:
                print(f"[ERROR] Failed to delete folder {folder}: {e}")

    if files_deleted == 0 and folders_deleted == 0:
        print("[INFO] No DB files or folders found to delete.")
    else:
        print(f"\n[SUMMARY] Total DB files deleted: {files_deleted}")
        print(f"[SUMMARY] Total folders deleted: {folders_deleted}")
        
    print("Cleanup complete.")

if __name__ == "__main__":
    delete_database_files()
    input("Press Enter to exit...")
