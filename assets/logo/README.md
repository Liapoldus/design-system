# Логотипы

`symbol.svg` — отдельный знак. `horizontal.svg` и `vertical.svg` включают
слоган; `horizontal-compact.svg` предназначен для тесной шапки без слогана.
`horizontal-on-dark.svg` и `app-icon.svg` рассчитаны на тёмную поверхность,
`app-icon-light.svg` — на светлую.

`app-icon.svg` и `app-icon-light.svg` — канонические исходники desktop-значков.
PNG 1024×1024 и Windows ICO 256×256 генерируются командой
`npm run build:native-icons` через `rsvg-convert` (`librsvg`). Логотипный текст
использует поставляемую гарнитуру Onest; в приложении вместе с SVG подключается
`fonts.css`.
