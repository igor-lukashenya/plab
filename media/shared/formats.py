"""Media formats: the single source of truth for canvas sizes.

The engine picks a project's format from the name of its parent folder
(media/<format>/<name>/), so a project never states its own dimensions.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Format:
    name: str
    width: int
    height: int
    default_duration: int  # seconds per slide/scene when a script does not set one
    kind: str              # "slides", "video" or "still"

    @property
    def orientation(self):
        return "portrait" if self.height > self.width else "landscape"


FORMATS = {f.name: f for f in (
    Format("deck", 1920, 1080, 8, "slides"),
    Format("invite", 1920, 1080, 6, "video"),
    Format("social", 1080, 1350, 5, "still"),
    Format("digest", 1920, 1080, 6, "video"),
    Format("shorts", 1080, 1920, 4, "video"),
    Format("explainer", 1920, 1080, 6, "video"),
)}
