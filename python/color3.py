import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Provided hex color list (sorted as requested: dark green to light green, white, light red to dark red)
hex_colors = [
    "00b31e", "05b522", "0ab727", "0fb92b", "14bb30", "18bd34", "1dbf38", "22c13d", "27c341", "2cc546", "31c64a", "36c84e", "3bca53", "40cc57", "45ce5c", "4ad060", "4ed264", "53d469", "58d66d", "5dd872", "62da76", "69dc7c", "71de83", "78e089", "7fe190", "87e396", "8ee59d", "95e7a3", "9de9aa", "a4ebb0", "acecb6", "b3eebd", "baf0c3", "c2f2ca", "c9f4d0", "d0f6d7", "d8f8dd", "dff9e4", "e6fbea", "eefdf1", "f5fff7", "f8fcf6", "ffffff", "fcf8f6", "fff5f5", "fff0f0", "ffebeb", "ffe7e7", "ffe2e2", "ffdddd", "ffd8d8", "ffd3d3", "ffcfcf", "ffcaca", "fec5c5", "fec0c0", "febbbb", "feb7b7", "feb2b2", "feadad", "fea8a8", "fea3a3", "fe9f9f", "fe9a9a", "fe9595", "fc8f8f", "fa8989", "f88383", "f67d7d", "f47878", "f27272", "f06c6c", "ee6666", "ec6060", "ea5a5a", "e85454", "e64e4e", "e44848", "e24242", "e03c3c", "de3737", "dc3131", "da2b2b", "d82525", "d61f1f"
]

# Plotting the color palette
num_colors = len(hex_colors)
fig, ax = plt.subplots(figsize=(3, num_colors * 0.3))
ax.set_xlim(0, 2)
ax.set_ylim(0, num_colors)
ax.axis('off')

# Adding color patches in the specified order
for idx, hex_color in enumerate(hex_colors):
    color_rect = mpatches.Rectangle((0, num_colors - idx - 1), 1, 1, color=f"#{hex_color}")
    ax.add_patch(color_rect)
    ax.text(1.2, num_colors - idx - 0.5, hex_color, ha="left", va="center", fontsize=8, color="black")

plt.show()