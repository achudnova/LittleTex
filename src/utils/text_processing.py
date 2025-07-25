from typing import Dict


def extract_metadata(markdown_content: str) -> tuple[dict, str]:
    """Extracts metadata from the top of the markdown file."""
    metadata: Dict[str, str] = {}
    lines = markdown_content.split("\n")

    content_start_index = 0
    in_metadata_block = True
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        if not in_metadata_block:
            break
        
        if stripped_line.startswith("@") and ":" in stripped_line:
            key, value = stripped_line[1:].split(":", 1)
            metadata[key.strip()] = value.strip()
            content_start_index = i + 1
            
        elif not stripped_line:
            content_start_index = i + 1
            
        else:
            in_metadata_block = False
    
    content_without_metadata = "\n".join(lines[content_start_index:])
    return metadata, content_without_metadata
        
    #     if stripped_line.startswith("@"):
    #         if ":" in stripped_line:
    #             key, value = stripped_line[1:].split(":", 1)
    #             metadata[key.strip()] = value.strip()
    #         content_start_index = i + 1
    #     elif not stripped_line:
    #         # Allow blank lines between metadata lines
    #         continue
    #     else:
    #         # First line of real content
    #         break

    # content_without_metadata = "\n".join(lines[content_start_index:])
    # return metadata, content_without_metadata
