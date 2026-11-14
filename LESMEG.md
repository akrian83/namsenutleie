# Namsen Utleie – nettsted

Statisk nettsted for namsenutleie.no. Ingen database, ingen abonnement.

- `build.py` inneholder all tekst, alle priser og alle lenker. Kjør `python3 build.py` for å bygge til `dist/`.
- `fetch-images.sh` (lages av `build.py`) henter bilder som mangler i `images/`.
- `.github/workflows/pages.yml` bygger og publiserer til GitHub Pages ved hver endring på `main`.

Booking og betaling skjer i Booqable (`namsen-utleie.booqableshop.com`). Nettstedet lenker rett til hvert produkt.

Nettadressene er de samme som på den gamle Wix-siden: `/utleie/`, `/adria-altea-552-pk-galleri/`,
`/snoskuter/`, `/henger/`, `/racing-simulator/`, `/om-oss/`, `/kontakt/`, `/vilkar/`.
