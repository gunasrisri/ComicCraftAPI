def build_comic_layout(outline: list[dict], stories: list[dict],
                       image_paths: list[str]) -> list[dict]:
    story_by_panel = {item["panel_number"]: item for item in stories}
    layout = []

    for index, panel in enumerate(outline, start=1):
        story = story_by_panel.get(index, {})
        layout.append({
            "panel_number": index,
            "title": panel.get("title", f"Panel {index}"),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", ""),
            "image_path": image_paths[index - 1],
            "caption": story.get("caption", ""),
            "narration": story.get("narration", ""),
            "dialogue": story.get("dialogue", ""),
        })

    return layout
