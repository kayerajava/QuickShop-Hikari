"""Arkeil look for QuickShop: writes overrides/tr_tr/messages.yml (deploy to plugins/QuickShop-Hikari/overrides/).

Only player-facing keys; the rest falls back to the bundled tr-TR / en-US files. Every key's {n} placeholders must match
the en-US source, which the self-check below enforces. Style follows ArkeilKira: gray text, white values, yellow money,
green success, red errors, glyph tags (Nexo arkeil_ui: PAZAR EB22, SATIYOR EB23, ALIYOR EB24)."""
import re
import sys
import yaml

PAZAR, SAT, AL = '', '', ''
EV, PARA, KUM, TAC, ANAH, SOL, SAG = 'ꐮ', 'ꑋ', 'ꐥ', 'ꐦ', 'ꐡ', '', ''
G, W, Y, OK, ERR, H = '<#9c9c9c>', '<white>', '<#F8E038>', '<#2ecc71>', '<#e55039>', '<#d1672e>'
P = f'<white>{PAZAR} '  # message prefix


def btn(label, color=H):
    return f' {G}[<bold>{color}{label}</bold>{G}]'


M = {
    # --- info panel (left/right click a shop) ---
    'menu.shop-information': f'<white>{PAZAR}',
    'menu.owner': f' {W}{TAC} {G}Sahibi: {W}{{0}}',
    'menu.item': f' {W}{EV} {G}Eşya: {W}{{0}}',
    'menu.preview': f'{G}[<#4AFFD7>Önizle{G}]',
    'menu.stock': f' {W}{EV} {G}Stok: {W}{{0}}',
    'menu.space': f' {W}{EV} {G}Boş yer: {W}{{0}}',
    'menu.price-per': f' {W}{PARA} {G}Tanesi: {Y}{{1}} {G}({W}{{0}}{G})',
    'menu.price-per-stack': f' {W}{PARA} {G}{W}{{2}}x {{0}}{G}: {Y}{{1}}',
    'menu.shop-stack': f' {W}{EV} {G}Paket: {W}{{0}} adet',
    'menu.total-value-of-chest': f' {W}{PARA} {G}Sandığın değeri: {Y}{{0}}',
    'menu.this-shop-is-selling': f' <white>{SAT} {G}Bu dükkân satıyor',
    'menu.this-shop-is-buying': f' <white>{AL} {G}Bu dükkân alıyor',
    'menu.this-shop-is-state': f' {W}{ANAH} {G}Durum: {{0}}',
    'menu.this-shop-is-frozen': f'{ERR}Kapalı',
    'menu.this-shop-is-active': f'{OK}Açık',
    'menu.enchants': f' {W}{EV} {G}Büyüler',
    'menu.stored-enchants': f' {W}{EV} {G}Kayıtlı büyüler',
    'menu.effects': f' {W}{EV} {G}Etkiler',
    'menu.damage-percent-remaining': f'{W}%{{0}} {G}sağlam',
    'menu.successful-purchase': f'{P}{OK}Satın aldın:',
    'menu.successfully-sold': f'{P}{OK}Sattın:',
    'menu.item-name-and-price': f' {W}{{0}}x {{1}} {G}→ {Y}{{2}}',
    'menu.item-name-and-price-tax': f' {W}{{0}}x {{1}} {G}→ {Y}{{2}} {G}({W}{{3}}{G} vergi)',
    'menu.sell-tax': f'{P}{G}Vergi: {Y}{{0}}',
    'menu.sell-tax-self': f'{P}{G}Kendi dükkânın, vergi yok.',
    'menu.item-holochat-error': f'{ERR}[Hata]',
    'menu.item-holochat-data-too-large': f'{ERR}[Eşya gösterilemeyecek kadar büyük]',
    'shop-information-not-shown-due-an-internal-error': f'{P}{ERR}Dükkân bilgisi eksik gösterilebilir, yetkililere haber ver.',

    # --- trading prompts and results ---
    'how-many-buy': f'{P}{G}Kaç tane {OK}alacağını{G} sohbete yaz. En fazla {W}{{0}}{G}, hepsi için {W}{{1}}{G}.',
    'how-many-sell': f'{P}{G}Kaç tane {Y}satacağını{G} sohbete yaz. En fazla {W}{{0}}{G}, hepsi için {W}{{1}}{G}.',
    'how-many-buy-stack': f'{P}{G}Kaç paket {OK}alacağını{G} yaz. Paket {W}{{0}}{G} adet, en fazla {W}{{1}}{G} paket, hepsi için {W}{{2}}{G}.',
    'how-many-sell-stack': f'{P}{G}Kaç paket {Y}satacağını{G} yaz. Paket {W}{{0}}{G} adet, en fazla {W}{{1}}{G} paket, hepsi için {W}{{2}}{G}.',
    'shop-purchase-cancelled': f'{P}{G}Alışveriş iptal edildi.',
    'no-pending-action': f'{P}{ERR}Bekleyen bir işlemin yok.',
    'you-cant-afford-to-buy': f'{P}{ERR}Paran yetmiyor: {W}{{0}}{ERR} gerekiyor, sende {W}{{1}}{ERR} var.',
    'the-owner-cant-afford-to-buy-from-you': f'{P}{ERR}Bu eşya {W}{{0}}{ERR} ediyor, dükkân sahibinde {W}{{1}}{ERR} var.',
    'not-enough-space': f'{P}{ERR}Envanterinde sadece {W}{{0}}{ERR} tanelik yer var.',
    'inventory-space-full': f'{P}{ERR}Envanterine en fazla {W}{{1}}{ERR} eşya daha sığar.',
    'shop-stock-too-low': f'{P}{ERR}Dükkânda sadece {W}{{0}} {{1}}{ERR} kaldı.',
    'shop-has-no-space': f'{P}{ERR}Dükkânda sadece {W}{{0}} {{1}}{ERR} için yer var.',
    'you-dont-have-that-many-items': f'{P}{ERR}Sende sadece {W}{{0}} {{1}}{ERR} var.',
    'purchase-out-of-stock': f'{P}{ERR}Dükkânın stoğu bitmiş.',
    'purchase-out-of-space': f'{P}{ERR}Dükkânın sandığı dolu.',
    'shop-owner-self-trade': f'{P}{G}Kendi dükkânınla alışveriş yapıyorsun, para kazanmazsın.',
    'shop-owner-self-trade-denied': f'{P}{ERR}Kendi dükkânınla alışveriş yapamazsın.',
    'shop-cannot-trade-when-freezing': f'{P}{ERR}Bu dükkân kapalı.',
    'trading-in-creative-mode-is-disabled': f'{P}{ERR}Yaratıcı modda alışveriş yapamazsın.',
    'shop-has-changed': f'{P}{ERR}Dükkân sen tıkladıktan sonra değişmiş, tekrar tıkla.',
    'negative-amount': f'{P}{ERR}Eksi miktar giremezsin.',
    'not-a-number': f'{P}{ERR}Sadece sayı yazabilirsin, sen {W}{{0}}{ERR} yazdın.',
    'not-a-integer': f'{P}{ERR}Tam sayı yazmalısın, sen {W}{{0}}{ERR} yazdın.',
    'thats-not-a-number': f'{P}{ERR}Geçersiz sayı.',
    'plugin-cancelled': f'{P}{ERR}İşlem iptal edildi: {W}{{0}}',
    'purchase-failed': f'{P}{ERR}Alışveriş yapılamadı, yetkililere haber ver.',
    'shop-transaction-failed': f'{P}{ERR}Alışveriş yapılamadı, hiçbir şey değişmedi. Sebep: {W}{{0}}',
    'economy-transaction-failed': f'{P}{ERR}Ödeme yapılamadı, hiçbir şey değişmedi. Yetkililere haber ver.',
    'integrations-check-failed-trade': f'{P}{ERR}Burada alışveriş yapılamaz ({W}{{0}}{ERR}).',
    'that-is-locked': f'{P}{ERR}Bu dükkân kilitli.',

    # --- owner notifications ---
    'player-bought-from-your-store': f'{P}{W}{{0}} {G}dükkânından {W}{{1}} {{2}}{G} aldı, {Y}{{3}}{G} kazandın.',
    'player-bought-from-your-store-tax': f'{P}{W}{{0}} {G}dükkânından {W}{{1}} {{2}}{G} aldı, {Y}{{3}}{G} kazandın ({W}{{4}}{G} vergi).',
    'player-sold-to-your-store': f'{P}{W}{{0}} {G}dükkânına {W}{{1}} {{2}}{G} sattı, {Y}{{3}}{G} ödedin.',
    'shop-out-of-stock': f'{P}{ERR}{{0}}, {{1}}, {{2}} konumundaki dükkânında {W}{{3}}{ERR} bitti.',
    'shop-out-of-stock-name': f'{P}{W}{{0}} {ERR}dükkânında {W}{{1}}{ERR} bitti.',
    'shop-out-of-space': f'{P}{ERR}{{0}}, {{1}}, {{2}} konumundaki dükkânın doldu.',
    'shop-out-of-space-name': f'{P}{W}{{0}} {ERR}dükkânın doldu.',
    'shop-freezed-at-location': f'{P}{W}{{0}} {G}dükkânın ({W}{{1}}{G}) kapatıldı.',
    'nothing-to-flush': f'{P}{G}Yeni dükkân mesajın yok.',
    'flush-finished': f'{P}{OK}Son mesajlar temizlendi.',

    # --- creating and managing ---
    'how-much-to-trade-for': f'{P}{G}{W}{{1}}x {{0}}{G} için fiyatı sohbete yaz.',
    'success-created-shop': f'{P}{OK}Dükkân kuruldu.',
    'shop-creation-cancelled': f'{P}{G}Dükkân kurulumu iptal edildi.',
    'success-removed-shop': f'{P}{G}Dükkân kaldırıldı.',
    'shop-already-owned': f'{P}{ERR}Burası zaten bir dükkân.',
    'you-cant-afford-a-new-shop': f'{P}{ERR}Dükkân kurmak {W}{{0}}{ERR} tutuyor, paran yetmiyor.',
    'reached-maximum-can-create': f'{P}{ERR}Dükkân sınırına ulaştın: {W}{{0}}/{{1}}',
    'no-double-chests': f'{P}{ERR}Çift sandıkla dükkân kurulamaz.',
    'invalid-container': f'{P}{ERR}Dükkân sadece envanteri olan bloklara kurulur.',
    'not-looking-at-shop': f'{P}{ERR}Bir dükkâna bakmıyorsun.',
    'not-looking-at-valid-shop-block': f'{P}{ERR}Buraya dükkân kurulamaz, sandığa bakarak tekrar dene.',
    'you-cant-create-shop-in-there': f'{P}{ERR}Burada dükkân kuramazsın.',
    'no-permission-build': f'{P}{ERR}Burada dükkân kuramazsın.',
    'integrations-check-failed-create': f'{P}{ERR}Burada dükkân kuramazsın ({W}{{0}}{ERR}).',
    'blacklisted-item': f'{P}{ERR}Bu eşya satılamaz.',
    'denied-put-in-item': f'{P}{ERR}Bu eşyayı dükkânına koyamazsın.',
    'chest-was-removed': f'{P}{ERR}Sandık kaldırıldı.',
    'failed-to-put-sign': f'{P}{ERR}Tabela için dükkânın önünde yer yok.',
    'no-anythings-in-your-hand': f'{P}{ERR}Elinde bir şey yok.',
    'price-too-cheap': f'{P}{ERR}Fiyat en az {W}{{0}}{ERR} olmalı.',
    'price-too-high': f'{P}{ERR}Fiyat en fazla {W}{{0}}{ERR} olabilir.',
    'digits-reach-the-limit': f'{P}{ERR}Fiyatta bu kadar küsurat olamaz.',
    'no-price-given': f'{P}{ERR}Geçerli bir fiyat yaz.',
    'no-price-change': f'{P}{ERR}Fiyat zaten bu.',
    'price-is-now': f'{P}{G}Yeni fiyat: {Y}{{0}}',
    'you-cant-afford-to-change-price': f'{P}{ERR}Fiyat değiştirmek {W}{{0}}{ERR} tutuyor.',
    'fee-charged-for-price-change': f'{P}{G}Fiyat değişikliği için {Y}{{0}}{G} ödedin.',
    'restricted-prices': f'{P}{ERR}{W}{{0}}{ERR} fiyatı en az {W}{{1}}{ERR}, en fazla {W}{{2}}{ERR}.',
    'restricted-price-max': f'{P}{ERR}{W}{{0}}{ERR} fiyatı en fazla {W}{{1}}{ERR}.',
    'restricted-price-min': f'{P}{ERR}{W}{{0}}{ERR} fiyatı en az {W}{{1}}{ERR}.',
    'buying-more-than-selling': f'{P}{ERR}Dikkat: aldığın fiyat sattığından yüksek.',
    'shop-now-freezed': f'{P}{G}Dükkânı kapattın, kimse alışveriş yapamaz.',
    'shop-nolonger-freezed': f'{P}{OK}Dükkânı yeniden açtın.',
    'not-managed-shop': f'{P}{ERR}Bu dükkânın sahibi ya da yetkilisi değilsin.',
    'no-permission': f'{P}{ERR}Bunu yapmaya iznin yok.',
    'permission-required': f'{P}{ERR}Bu dükkânda {W}{{0}}{ERR} iznin yok.',
    'refill-success': f'{P}{OK}Dükkân dolduruldu.',
    'empty-success': f'{P}{OK}Dükkân boşaltıldı.',
    'shop-name-success': f'{P}{G}Dükkânın adı artık {W}{{0}}',
    'shop-name-unset': f'{P}{G}Dükkânın adı kaldırıldı.',
    'shop-staff-added': f'{P}{W}{{0}} {G}dükkânına yetkili olarak eklendi.',
    'shop-staff-deleted': f'{P}{W}{{0}} {G}dükkânının yetkililerinden çıkarıldı.',
    'shop-staff-cleared': f'{P}{G}Dükkânının bütün yetkilileri çıkarıldı.',
    'shop-staff-empty': f'{P}{G}Bu dükkânın yetkilisi yok.',
    'delete-controlpanel-button-confirm': f'{P}{ERR}Dükkânı kaldırmak için {W}{{0}}{ERR} saniye içinde {W}[Kaldır]{ERR} tuşuna tekrar bas.',
    'shops-arent-locked': f'{P}{G}Dükkânın hırsızlığa karşı kilitli değil.',
    'average-price-nearby': f'{P}{G}Yakındaki ortalama fiyat: {Y}{{0}}',

    # --- sign (4 lines) ---
    'signs.header': '{1}{0}',
    'signs.header-available': f'{{0}}',
    'signs.header-unavailable': f'<dark_red>{{0}}',
    'signs.selling': f'<white>{SAT}</white> {{0}}',
    'signs.buying': f'<white>{AL}</white> {{0}}',
    'signs.stack-selling': f'<white>{SAT}</white> {{0}}',
    'signs.stack-buying': f'<white>{AL}</white> {{0}}',
    'signs.price': '{0}',
    'signs.stack-price': '{1}x {2}: {0}',
    'signs.out-of-stock': '<dark_red>Stok bitti',
    'signs.out-of-space': '<dark_red>Sandık dolu',
    'signs.unlimited': 'Sınırsız',
    'signs.freeze': '<dark_red>Kapalı',
    'signs.item-duration': 'Süre: {0}',
    'signs.item-level': 'Seviye: {0}',
    'signs.splash-potion': 'Atılan',
    'signs.linger-potion': 'Kalıcı',

    # --- control panel (owner right-clicks own shop with sneak) ---
    'controlpanel.infomation': f'<white>{PAZAR} {G}Dükkân ayarları',
    'controlpanel.setowner': f' {W}{TAC} {G}Sahibi: {W}{{0}}' + btn('Değiştir'),
    'controlpanel.setowner-hover': f'{G}Sahibi değiştir',
    'controlpanel.item': f' {W}{EV} {G}Eşya: {W}{{0}}' + btn('Değiştir'),
    'controlpanel.item-hover': f'{G}Elindeki eşyayı sat',
    'controlpanel.price': f' {W}{PARA} {G}Fiyat: {Y}{{0}}' + btn('Değiştir'),
    'controlpanel.price-hover': f'{G}Yeni fiyat yaz',
    'controlpanel.stack': f' {W}{EV} {G}Paket: {W}{{0}} adet' + btn('Değiştir'),
    'controlpanel.stack-hover': f'{G}Paketteki adet; normal satış için 1',
    'controlpanel.mode-selling': f' <white>{SAT} {G}Satış dükkânı' + btn('Alışa çevir'),
    'controlpanel.mode-selling-hover': f'{G}Dükkânı oyunculardan alan dükkâna çevir',
    'controlpanel.mode-buying': f' <white>{AL} {G}Alış dükkânı' + btn('Satışa çevir'),
    'controlpanel.mode-buying-hover': f'{G}Dükkânı oyunculara satan dükkâna çevir',
    'controlpanel.freeze': f' {W}{ANAH} {G}Kapalı: {W}{{0}}' + btn('Aç/Kapat'),
    'controlpanel.freeze-hover': f'{G}Dükkânı alışverişe aç veya kapat',
    'controlpanel.lock': f' {W}{ANAH} {G}Kilit: {W}{{0}}' + btn('Aç/Kapat'),
    'controlpanel.lock-hover': f'{G}Sandığı başkalarına kilitle',
    'controlpanel.toggledisplay': f' {W}{EV} {G}Üstteki eşya: {W}{{0}}' + btn('Aç/Kapat'),
    'controlpanel.toggledisplay-hover': f'{G}Sandığın üstünde dönen eşyayı göster/gizle',
    'controlpanel.currency': f' {W}{PARA} {G}Para birimi: {W}{{0}}' + btn('Ayarla'),
    'controlpanel.currency-hover': f'{G}Dükkânın para birimini ayarla',
    'controlpanel.unlimited': f' {W}{EV} {G}Sınırsız: {W}{{0}}' + btn('Değiştir'),
    'controlpanel.unlimited-hover': f'{G}Sınırsız stok aç/kapat',
    'controlpanel.alwayscounting': f' {W}{EV} {G}Hep say: {W}{{0}}' + btn('Değiştir'),
    'controlpanel.alwayscounting-hover': f'{G}Sandığın içeriğini her seferinde say',
    'controlpanel.inventory': f' {W}{EV} {G}Sandık' + btn('Aç'),
    'controlpanel.inventory-hover': f'{G}Dükkânın sandığını aç',
    'controlpanel.history': f' {W}{KUM} {G}Geçmiş' + btn('Gör'),
    'controlpanel.history-hover': f'{G}Dükkânın alışveriş geçmişi',
    'controlpanel.refill': f' {W}{EV} {G}Doldur' + btn('Tamam'),
    'controlpanel.refill-hover': f'{G}Dükkânı doldur',
    'controlpanel.empty': f' {W}{EV} {G}Boşalt' + btn('Tamam'),
    'controlpanel.empty-hover': f'{G}Dükkânın sandığını boşalt',
    'controlpanel.remove': f' {W}{EV} {G}Dükkân' + btn('Kaldır', ERR),
    'controlpanel.remove-hover': f'{ERR}Dükkânı kaldır',

    # --- words used inside other lines ---
    'shop-type.selling': 'SATIŞ',
    'shop-type.buying': 'ALIŞ',
    'shop-type.frozen': 'KAPALI',
    'shop-state.frozen': 'KAPALI',
    'shop-state.unfrozen': 'AÇIK',
    'shop-state.freeze': 'Kapat',
    'shop-state.unfreeze': 'Aç',
    'shop-display.enabled': 'Açık',
    'shop-display.disabled': 'Kapalı',
    # the info panel frame: no box, just a dark rule above and below
    'tableformat.full_line': '<#3b3b3b>' + '─' * 22,
    'tableformat.left_half_line': '<#3b3b3b>' + '─' * 10,
    'tableformat.right_half_line': '<#3b3b3b>' + '─' * 10,
    'tableformat.left_begin': '',
    'booleanformat.success': f'{OK}Evet',
    'booleanformat.failed': f'{ERR}Hayır',
    'admin-shop': 'Sunucu',
    'unknown-owner': 'Bilinmiyor',
    'chest-title': 'Dükkân',
}


def nest(flat):
    out = {}
    for key, value in flat.items():
        node = out
        *parents, leaf = key.split('.')
        for part in parents:
            node = node.setdefault(part, {})
        node[leaf] = value
    return out


def flatten(d, prefix=''):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, prefix + k + '.'))
        else:
            out[prefix + k] = v
    return out


if __name__ == '__main__':
    en = flatten(yaml.safe_load(open(sys.argv[1], encoding='utf-8')))
    bad = []
    for key, value in M.items():
        if key not in en:
            bad.append((key, 'unknown key'))
            continue
        want = sorted(set(re.findall(r'\{\d+\}', str(en[key]))))
        got = sorted(set(re.findall(r'\{\d+\}', value)))
        if want != got:
            bad.append((key, want, got))
    assert not bad, bad
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write('# Arkeil: generated by arkeil/overrides.py in the QuickShop fork. Edit there, not here.\n')
        yaml.safe_dump(nest(M), f, allow_unicode=True, width=10_000, sort_keys=False)
    print(len(M), 'keys ok')
