YBIT_YIN = 0  # 8
YBIT_YANG = 1  # 7
YBIT_OLD_YIN = 2  # 6
YBIT_OLD_YANG = 3  # 9
YBIT_EMPTY = 4  # 5

YBIT_SVG = [
    """
      <rect width="60" height="15" y="4" class="ybit-line" />
      <rect width="60" height="15" y="4" x="100" class="ybit-line" />
  """,
    """
      <rect width="160" height="15" y="4" class="ybit-line" />
  """,
    """
      <rect width="60" height="15" y="4" x="100" class="ybit-line" />
      <rect width="60" height="15" y="4" class="ybit-line" />
      <line x1="70" y1="4"  x2="90" y2="18" class="ybit-cross"/>
      <line x1="90" y1="4"  x2="70" y2="18" class="ybit-cross"/>
  """,
    """
      <rect width="60" height="15" y="4" x="100" class="ybit-line" />
      <rect width="60" height="15" y="4" class="ybit-line" />
      <circle cx="80" cy="12" r="7" y="4" class="ybit-circle" />
  """,
    """
      <line x1="0" y1="6" x2="160" y2="6" stroke-dasharray="14,2" class="ybit-empty" />
      <line x1="0" y1="18" x2="160" y2="18" stroke-dasharray="14,2" class="ybit-empty" />
      <line x1="2" y1="12" x2="2" y2="15" class="ybit-empty" />
      <line x1="155" y1="12" x2="155" y2="15" class="ybit-empty" />
  """,
]
