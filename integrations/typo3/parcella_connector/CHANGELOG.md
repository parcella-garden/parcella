# Changelog

## 1.1.0

- The draft image gets the alt text set in Parcella (Website Plugin
  Protocol v1, optional `image_alt` field) instead of always the title;
  without one it still falls back to the title. An alt-text-only change
  in Parcella updates the existing image's alt text without replacing
  the image.

## 1.0.0

- First release: receives drafts from Parcella (Website Plugin Protocol v1)
  as hidden EXT:news records with FAL image, for TYPO3 12.4 and 13.4 LTS.
