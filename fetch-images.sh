#!/bin/sh
# Henter bilder som mangler i images/. Kjøres av GitHub Actions.
set -u
mkdir -p images
[ -s "images/snoskuter-hero.jpg" ] || curl -fsSL --retry 3 -o "images/snoskuter-hero.jpg" "https://static.wixstatic.com/media/fcca76_0763720b8c004f38adf46616ff1198a3~mv2.jpeg" || echo "MANGLER: snoskuter-hero.jpg"
[ -s "images/adria-eksterior-1.jpg" ] || curl -fsSL --retry 3 -o "images/adria-eksterior-1.jpg" "https://static.wixstatic.com/media/fcca76_e4ff55a4c86b4eacba7f2e4e50ad6335~mv2.jpg" || echo "MANGLER: adria-eksterior-1.jpg"
[ -s "images/adria-eksterior-2.jpg" ] || curl -fsSL --retry 3 -o "images/adria-eksterior-2.jpg" "https://static.wixstatic.com/media/fcca76_637696227d964964a059dca22c9a4ce3~mv2.jpg" || echo "MANGLER: adria-eksterior-2.jpg"
[ -s "images/adria-eksterior-3.jpg" ] || curl -fsSL --retry 3 -o "images/adria-eksterior-3.jpg" "https://static.wixstatic.com/media/fcca76_e2e605eae9bf41de806890cb89f20763~mv2.jpg" || echo "MANGLER: adria-eksterior-3.jpg"
[ -s "images/adria-eksterior-4.jpg" ] || curl -fsSL --retry 3 -o "images/adria-eksterior-4.jpg" "https://static.wixstatic.com/media/fcca76_0f980ecfc2794ceaa837dad039db092b~mv2.jpg" || echo "MANGLER: adria-eksterior-4.jpg"
[ -s "images/adria-interior-1.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-1.jpg" "https://static.wixstatic.com/media/fcca76_822f3fe4449e48af8679467504222baa~mv2.jpg" || echo "MANGLER: adria-interior-1.jpg"
[ -s "images/adria-interior-2.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-2.jpg" "https://static.wixstatic.com/media/fcca76_4f264f7bc7f8478bae3b959468ee1897~mv2.jpg" || echo "MANGLER: adria-interior-2.jpg"
[ -s "images/adria-interior-3.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-3.jpg" "https://static.wixstatic.com/media/fcca76_46db76e4f102430eab62807a63f9f028~mv2.jpg" || echo "MANGLER: adria-interior-3.jpg"
[ -s "images/adria-interior-4.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-4.jpg" "https://static.wixstatic.com/media/fcca76_4c391daafe11426d835108dc2790c87c~mv2.jpg" || echo "MANGLER: adria-interior-4.jpg"
[ -s "images/adria-interior-5.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-5.jpg" "https://static.wixstatic.com/media/fcca76_43382aaf37fb4bcd861e69f44bdc9aee~mv2.jpg" || echo "MANGLER: adria-interior-5.jpg"
[ -s "images/adria-interior-6.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-6.jpg" "https://static.wixstatic.com/media/fcca76_1342e13ea0704ebebdb81e3177517f27~mv2.jpg" || echo "MANGLER: adria-interior-6.jpg"
[ -s "images/adria-interior-7.jpg" ] || curl -fsSL --retry 3 -o "images/adria-interior-7.jpg" "https://static.wixstatic.com/media/fcca76_d60fd7d69fff448995cfe270fd6b3cc3~mv2.jpg" || echo "MANGLER: adria-interior-7.jpg"
[ -s "images/polaris-sks.jpg" ] || curl -fsSL --retry 3 -o "images/polaris-sks.jpg" "https://content.booqablecdn.com/uploads/59647ca9ef31fb77bc74ed95fc675be5/photo/photo/f45aefd1-b529-4f1c-bcc1-68490b3839df/polaris-800-sks.jpeg" || echo "MANGLER: polaris-sks.jpg"
[ -s "images/polaris-rmk.jpg" ] || curl -fsSL --retry 3 -o "images/polaris-rmk.jpg" "https://content.booqablecdn.com/uploads/59647ca9ef31fb77bc74ed95fc675be5/photo/photo/80e0c6dc-03fd-4e4d-b6a6-0432120728d5/polaris-850-pro-rmk.jpeg" || echo "MANGLER: polaris-rmk.jpg"
[ -s "images/henger.jpg" ] || curl -fsSL --retry 3 -o "images/henger.jpg" "https://content.booqablecdn.com/uploads/59647ca9ef31fb77bc74ed95fc675be5/photo/photo/fdd4f653-6222-4f94-8182-f865110a1839/henger-innside.jpeg" || echo "MANGLER: henger.jpg"
