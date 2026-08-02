# CNCF Icons

[![GitHub Pages](https://github.com/jajera/cncf-icons/actions/workflows/deploy.yml/badge.svg)](https://jajera.github.io/cncf-icons/)

A searchable web library for browsing and copying CNCF project icons and
official Kubernetes architecture icons.

## Features

- Search by project or resource name, tags, or common abbreviations
- Filter by project / Kubernetes category tags
- Copy SVG or PNG data to the clipboard
- Download icons as SVG or PNG
- Light and dark themes
- Responsive layout for desktop and mobile
- Shareable search and tag filters in the URL

## Statistics

- **168** total SVG icons
  - **96** CNCF project artwork icons (color / black / white, plus a few
    special variants)
  - **72** Kubernetes architecture icons (resources, control plane,
    infrastructure; labeled and unlabeled where available)

## Usage

Serve the repository from a local web server:

```shell
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

Use the search box or tags to find an icon. Hover over a card to copy or
download its SVG or PNG representation. White-variant icons render on a dark
tile so they stay visible in light mode.

## Repository structure

```text
icons/
  <project>/              CNCF project icons (color / black / white)
  k8s-resources/          Kubernetes resource icons
  k8s-control-plane/      Kubernetes control plane icons
  k8s-infrastructure/     Kubernetes infrastructure icons
icons.json                Searchable icon metadata used by the web app
favicon.svg               Site favicon (Kubernetes mark)
og-image.svg              Open Graph image source
og-image.png              Open Graph / social preview image (rendered)
scripts/                  Metadata generation tooling
```

Regenerate `icons.json` after adding or renaming an icon:

```shell
python3 scripts/generate_icons_json.py
```

## Attribution

CNCF project icons come from
[cncf/artwork](https://github.com/cncf/artwork).
Kubernetes architecture icons come from
[kubernetes/community](https://github.com/kubernetes/community)
(`icons/svg`). Project names and logos are trademarks of their respective
owners / the CNCF. Follow each project's brand guidelines when using the
marks.

## License

The website code is available under the [MIT License](LICENSE). Icon assets
remain subject to their upstream CNCF / Kubernetes licensing and brand terms
and are not relicensed under MIT.
