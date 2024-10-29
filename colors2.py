import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Provided hex color list (partial, you can add the full list)
hex_colors = [
	"63BE7B","67C07E", "69C180", "6AC181", "6BC182", "6BC282", "6DC284", "6EC384", "70C386", "71C487", "72C488", "73C589", "74C58A", "76C68C", "78C78D", "79C78E", "7BC890", "7DC991", "80CA94", "81CB95", "82CB96", "85CC98", "85CC99", "87CD9A", "88CD9B", "89CE9C", "8ACE9C", "8DCF9F", "8DCFA0", "90D0A2", "91D1A3", "95D3A6", "96D3A7", "97D4A8", "99D4AA", "9CD5AC", "9DD6AD", "9DD6AE", "9FD7AF", "A0D7AF", "A1D7B0", "A1D8B1", "A2D8B1", "A2D8B2", "A3D8B2", "A5D9B4", "A6D9B5", "A6DAB5", "A7DAB5", "A7DAB6", "A8DAB7", "A9DAB7", "A9DBB7", "A9DBB8", "AADBB9", "ABDBB9", "ACDCBA", "ADDCBB", "AEDCBB", "AEDDBC", "AFDDBC", "AFDDBD", "B0DDBD", "B1DEBE", "B2DEBF", "B2DEC0", "B3DFC0", "B4DFC1", "B5E0C2", "B6E0C3", "B7E0C4", "B8E1C5", "B9E1C5", "B9E1C6", "BAE1C6", "BBE2C7", "BCE2C7", "BCE2C8", "BDE3C8", "BDE3C9", "BEE3C9", "BEE3CA", "BFE3CA", "BFE4CA", "BFE4CB", "C0E4CC", "C1E4CC", "C2E5CD", "C3E5CD", "C3E5CE", "C4E6CF", "C5E6CF", "C5E6D0", "C6E6D0", "C6E6D1", "C7E7D1", "C7E7D2", "C8E7D2", "C8E7D3", "C9E8D3", "CAE8D4", "CBE8D4", "CBE9D5", "CCE9D6", "CDE9D6", "CDE9D7", "CEE9D7", "CEEAD7", "CFEAD8", "CFEAD9", "D0EAD9", "D0EBDA", "D1EBDA", "D2EBDB", "D3ECDB", "D3ECDC", "D4ECDC", "D4ECDD", "D5ECDD", "D5EDDE", "D6EDDE", "D6EDDF", "D7EDDF", "D8EEE0", "D9EEE1", "DAEEE1", "DAEEE2", "DAEFE2", "DBEFE2", "DBEFE3", "DCEFE3", "DCEFE4", "DDF0E4", "DEF0E5", "DEF0E6", "DFF0E6", "DFF1E6", "E0F1E6", "E0F1E7", "E1F1E7", "E1F1E8", "E2F2E8", "E2F2E9", "E3F2E9", "E3F2EA", "E4F2EA", "E4F3EA", "E4F3EB", "E5F3EB", "E5F3EC", "E6F3EC", "E6F4EC", "E7F4ED", "E8F4EE", "E9F4EE", "E9F5EF", "EAF5EF", "EAF5F0", "EBF5F0", "EBF6F1", "ECF6F1", "EDF6F2", "EEF6F3", "EEF7F3", "EFF7F4", "F0F7F4", "F0F7F5", "F0F8F5", "F1F8F6", "F2F8F6", "F2F8F7", "F3F8F7", "F3F9F7", "F4F9F8", "F5F9F9", "F5FAF9", "F6FAFA", "F7FAFB", "F8FBFC", "F9FBFC", "F8696B", "F86A6C", "F86B6D", "F86D6F", "F86E70", "F86F71", "F87072", "F87274", "F87375", "F87476", "F87678", "F8777A", "F8787A", "F8797B", "F87A7C", "F87B7D", "F87C7E", "F87D7F", "F87E80", "F88082", "F88183", "F88385", "F88386", "F88486", "F88587", "F88588", "F88688", "F8878A", "F8888A", "F8898C", "F88A8D", "F88D8F", "F98D90", "F98E90", "F98F91", "F99092", "F99295", "F99395", "F99396", "F99496", "F99598", "F99698", "F9979A", "F9989B", "F9999B", "F99A9C", "F99B9D", "F99C9E", "F99DA0", "F99EA1", "F99FA1", "F9A0A2", "F9A2A4", "F9A2A5", "F9A3A5", "F9A3A6", "F9A4A6", "F9A5A7", "F9A6A9", "F9A7A9", "F9A8AA", "F9A8AB", "F9A9AC", "F9AAAC", "F9ABAE", "F9ACAF", "F9ADAF", "F9ADB0", "F9AEB0", "F9AEB1", "F9AFB1", "F9B0B2", "F9B0B3", "F9B1B3", "F9B1B4", "F9B2B4", "F9B3B5", "F9B3B6", "F9B4B7", "F9B5B8", "F9B6B9", "F9B7BA", "F9B8BC", "F9B9BD", "F9BABE", "F9BBBF", "F9BCC0", "F9BDC1", "F9BEC2", "F9BFC3", "F9C0C4", "F9C1C5", "F9C2C6", "F9C3C7", "F9C4C8", "F9C5C9", "F9C6CA", "F9C7CB", "F9C8CC", "F9C9CD"
]

# Plotting the color palette
num_colors = len(hex_colors)
fig, ax = plt.subplots(figsize=(15, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, num_colors // 10 + 1)
ax.axis('off')

# Adding color patches
for idx, hex_color in enumerate(hex_colors):
    row = idx // 10
    col = idx % 10
    color_rect = mpatches.Rectangle((col, row), 1, 1, color=f"#{hex_color}")
    ax.add_patch(color_rect)
    ax.text(col + 0.5, row + 0.5, hex_color, ha="center", va="center", fontsize=8, color="black")

plt.show()

