# Skrifter for karusellen

Karusellen brukar **Lato** (Black / Bold / Regular) til overskrifter og tekst —
same skrift som i Bolk-malen. Generatoren bundlar skrifta via `@font-face`, så
ho ser lik ut overalt karusellen blir bygd (Cowork-sandkassa, Hetzner, lokalt),
utan å vera avhengig av kva som tilfeldigvis er installert på maskina.

## Kva som må liggja her

```
assets/fonts/Lato-Black.ttf
assets/fonts/Lato-Bold.ttf
assets/fonts/Lato-Regular.ttf
```

Når desse tre filene finst, vevjar `build_carousel.py` dei inn automatisk.
Manglar dei, fell generatoren tilbake på systemets sans-stack (t.d. DejaVu) og
skriv ei åtvaring — layouten er den same, men overskriftene ser ikkje heilt
endelege ut.

## Henta skriftene

Lato er lisensiert under SIL Open Font License 1.1 (fri å bundla). Køyr:

```bash
bash assets/fonts/fetch-fonts.sh
```

Skriptet hentar dei tre vektane frå Google Fonts-repoet til denne mappa. Treng
nett-tilgang. (I sandkassar utan nett må filene leggjast inn manuelt.)
