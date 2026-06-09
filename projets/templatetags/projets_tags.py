from decimal import Decimal
from django import template

register = template.Library()

TAUX_VERS_XOF = {
    'XOF': Decimal('1'),
    'USD': Decimal('615.00'),
    'EUR': Decimal('655.957'),
    'GBP': Decimal('775.00'),
    'JPY': Decimal('4.10'),
    'CHF': Decimal('685.00'),
    'CNY': Decimal('85.00'),
    'UC':  Decimal('769.083'),
}

SYMBOLE = {
    'XOF': 'FCFA',
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'UC':  'UC',
}


def _fmt(v):
    """Formate un flottant en Mds / M / K avec au plus 2 décimales significatives."""
    if v is None:
        return '—'
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v == 0:
        return '0'
    abs_v = abs(v)
    sign = '-' if v < 0 else ''
    if abs_v >= 1_000_000_000_000:
        n = abs_v / 1_000_000_000_000
        s = f"{n:.2f}".rstrip('0').rstrip('.')
        return f"{sign}{s} Brd"
    if abs_v >= 1_000_000_000:
        n = abs_v / 1_000_000_000
        s = f"{n:.2f}".rstrip('0').rstrip('.')
        return f"{sign}{s} Mds"
    if abs_v >= 1_000_000:
        n = abs_v / 1_000_000
        s = f"{n:.2f}".rstrip('0').rstrip('.')
        return f"{sign}{s} M"
    if abs_v >= 1_000:
        n = abs_v / 1_000
        s = f"{n:.1f}".rstrip('0').rstrip('.')
        return f"{sign}{s} K"
    return f"{sign}{round(abs_v):,}"


@register.filter(name='fmt_montant')
def fmt_montant(value, devise=''):
    """
    Formate un montant avec unité lisible : 45 M, 1.65 Mds, 456 K.
    Usage : {{ projet.montant_total|fmt_montant:projet.devise }}
    """
    s = _fmt(value)
    if devise:
        return f"{s} {devise}"
    return s


@register.filter(name='fmt_fcfa')
def fmt_fcfa(value):
    """Formate un montant FCFA (XOF) avec unité lisible."""
    s = _fmt(value)
    if s in ('—', '0'):
        return s
    return f"{s} FCFA"


@register.filter(name='to_fcfa')
def to_fcfa(value, devise='XOF'):
    """
    Convertit un montant depuis une devise vers FCFA.
    Usage : {{ montant|to_fcfa:devise }}
    """
    try:
        montant = Decimal(str(value))
        taux = TAUX_VERS_XOF.get(str(devise).upper(), Decimal('1'))
        return montant * taux
    except Exception:
        return value


@register.filter(name='to_fcfa_fmt')
def to_fcfa_fmt(value, devise='XOF'):
    """Convertit en FCFA et formate directement."""
    try:
        montant = Decimal(str(value))
        taux = TAUX_VERS_XOF.get(str(devise).upper(), Decimal('1'))
        return fmt_fcfa(montant * taux)
    except Exception:
        return str(value)


@register.filter(name='devise_symbole')
def devise_symbole(devise):
    """Retourne le symbole court d'une devise."""
    return SYMBOLE.get(str(devise).upper(), str(devise))


@register.filter(name='as_pct')
def as_pct(value):
    """
    Normalise un taux en pourcentage pour l'affichage.
    Si la valeur est une fraction (0 < v < 1), multiplie par 100.
    Usage : {{ projet.taux_avancement|as_pct }}
    """
    try:
        v = float(value)
        if 0 < v < 1:
            return round(v * 100, 1)
        return round(v, 1)
    except (TypeError, ValueError):
        return 0


@register.filter(name='split_comma')
def split_comma(value):
    """Découpe une chaîne séparée par des virgules et renvoie une liste nettoyée."""
    if not value:
        return []
    return [z.strip() for z in str(value).split(',') if z.strip()]
