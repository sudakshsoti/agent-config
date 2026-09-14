# Precision software reference

Primary reference: an Attio records table with the workspace sidebar. Three companion captures show the other operational surfaces this language needs: a Linear board of cards, an Attio report builder with a configuration panel, and an Attio template dialog over the app.

All four are user-supplied viewport captures of the live applications at 2× device pixel ratio, 1512 × 945 CSS px, downscaled to CSS pixels on 2026-09-14. Values below were measured from the images and are approximate.

## 1. Records table with sidebar (primary)

- Page title: Companies – Attio
- Source: https://app.attio.com/ (workspace view, captured by the user)
- Image: [reference.png](reference.png)
- Captured: 2026-09-14

| Relationship | Value in the reference |
| --- | --- |
| Sidebar | 275px wide on a near-white ground (#FCFCFC) with a 1px right border; items at about 13px on a 29px pitch with a 16px icon; section labels ("Favorites", "Records", "Lists") in grey with a disclosure chevron |
| Top bar | 48px; the object name at about 17px weight 600 with an info icon; avatar and actions at the right |
| Toolbar | a second 48px row: the view selector as a pill at the left, "View settings" and "Import / Export" as text buttons at the right; then a 53px row holding "Sort" and "Filter" as 32px pills |
| Table header | 36px tall, column names at about 13px weight 500 with a type icon before each; column widths 250, 287, 180, 180 and 215px, resizable |
| Rows | 36px pitch, 1px rules, text at about 14px; the name column holds a checkbox, a 16px logo and the name; the selected row is tinted lavender (#E4E9FF) |
| Cell types | chips in pale tints with text in the same hue darker, clipped with an ellipsis at the cell edge; links underlined; empty values as grey "No contact"; a status dot before "No communication"; counts right-aligned |
| Footer row | "10 count" right-aligned under the name column, "Add calculation" placeholders in grey under the rest |
| Primary action | one blue (about #4C70D4) for the "Add billing" button and the trial count; nothing else in the chrome is coloured |
| Colour | white table, near-white sidebar, black text, grey secondary; colour comes from chips, logos and status dots only |

## 2. Board of cards (Linear)

- Page title: Issues – Linear
- Source: https://linear.app/ (workspace board, captured by the user)
- Image: [reference-board.png](reference-board.png)
- Captured: 2026-09-14

| Relationship | Value in the reference |
| --- | --- |
| Frame | sidebar 245px on #F3F3F3; the main view is a white panel with a 1px border and 8px radius inset from the sidebar and the window edge |
| Header | 55px with a breadcrumb at about 14px, star and overflow; a 40px tab row beneath ("Overview", "Updates", "Issues") with the active tab in a filled pill; filter and display icons at the right, one with a blue dot |
| Columns | 348px pitch, cards 322px wide (x=261, x=609, x=957) with a 26px gap; a column header 35px tall with status icon, name at about 13px weight 500 and count in grey; a 200px "Hidden columns" list at the right |
| Cards | 116px tall on a 126px pitch (10px gap), white with 1px border and 8px radius, 12px padding |
| Card anatomy | identifier in a small monospace at 11px; title at about 14px 20px below it with the status icon before it; a row of 24px chips (priority, date, labels with a coloured dot) 31px below; "Created Mar 31" in grey 30px below that; assignee placeholder top-right |
| Status colour | the status icon carries the colour (yellow half-circle, blue check); label dots use one hue per label; cards themselves stay white |
| Footer | a 48px strip with the filter summary centred: "1 issue hidden by filters  Clear Filters ×" |
| Colour | greys for chrome, black text, one blue for the active-filter dot and links; labels and states are the only saturated colour |

## 3. Chart with a configuration panel (Attio)

- Page title: New report – Attio
- Source: https://app.attio.com/ (report builder, captured by the user)
- Image: [reference-report.png](reference-report.png)
- Captured: 2026-09-14

| Relationship | Value in the reference |
| --- | --- |
| Frame | the report is a white panel with a 1px border inset 8px from the sidebar, spanning to the window edge; a 48px header holds "New report" at about 17px weight 600, "Discard changes" as text and "Save" as a 32px blue button |
| Split | chart area x=284 to x=1103, configuration panel 400px wide at the right with a 1px divider; a 40px footer strip under the chart with "Calculated values" left and "View contributing data" right |
| Chart | stacked bars 108px wide on a 120px pitch, gridlines dotted, axis labels at 13px, legend as 8px squares with 13px labels 48px above the plot; series colours are pastel and consistent with the chips in the table |
| Panel groups | each setting group in a bordered box with 8px radius and 12px padding, 14px apart; a label at about 12px grey, then a 34px select with icon, value and chevron, 8px below |
| Toggles | 36px switches in the accent blue with a 14px label; three stacked on a 32px pitch under "Visualization" |
| Removable groups | "Grouped by" and "Segmented by" carry an × at the top-right of their box |
| Colour | white panel, grey borders, black text; blue only for Save, toggles and the trial count; the chart holds all other colour |

## 4. Dialog over the app (Attio)

- Page title: Templates – Attio
- Source: https://app.attio.com/ (template picker, captured by the user)
- Image: [reference-dialog.png](reference-dialog.png)
- Captured: 2026-09-14

| Relationship | Value in the reference |
| --- | --- |
| Scrim and modal | the app dims to about 26% black; the dialog is 1244 × 787px, white, 12px radius, centred horizontally and 79px from the top |
| Header | 49px with the title at about 14px weight 500 at the left and a close × at the right, 1px rule beneath |
| Split | a 261px filter list at the left with a "USE CASES" label in 11px caps; rows at 15px on a 40px pitch, a 24px tinted icon tile before each and a 20px checkbox at the right, checked in the accent blue |
| Search | a 36px field at the top of the right pane with placeholder text at 16px, no border, 1px rule beneath |
| Result cards | 946px wide, about 140px tall on a 142px pitch, 1px border, 8px radius, 12px padding; a 143 × 95px thumbnail at the left, title at 15px weight 500, two lines of description at 13px on a 17px pitch, chips 34px below; an icon row with a "+4" overflow count at the top-right |
| Footer | 48px with a "Navigate" hint and ↑↓ key caps at the left; an outlined "Start from Scratch" and a blue "Preview template" button, 32px tall, each with a ↵ key cap, at the right |
| Colour | white dialog, grey rules and hints; blue only for checks and the primary button; chips tinted by category |

## Borrow

A sidebar one step off white with a single border; a table whose header and rows share one pitch and one text size; chips as pale tints with darker text of the same hue; empty values as grey text rather than blanks; a selected row as a tint, not a border; a card as identifier, title, chip row and meta line on a fixed rhythm; status carried by an icon or dot, never by a coloured card; a configuration panel of bordered groups with label-then-control; a dialog with a filter pane, a search field and a footer that names its keys; one blue for primary actions and checks.

## Do not borrow

Attio's and Linear's logos, trial banners and onboarding counters; the demo data; a 245–275px sidebar when the artifact has fewer than five destinations; chips as decoration on text that is not a category; a dialog this large for a two-field form; the pastel series palette where series have a defined meaning. Keep the working surface compact and purposeful.
