# 🚀 Quick Reference: Visualization Tab Integration

## One-Line Summary
**Material Browser and Visualization tab are now fully linked - select a material there, it auto-selects here!**

---

## 🎯 What Changed

### Before
```
Material Browser: Select "Copper"
Visualization Tab: Manually find and select "Copper" again
```

### After (NOW)
```
Material Browser: Select "Copper"
Visualization Tab: "Copper" already selected ✓
```

---

## 📋 Quick Usage

### Basic Workflow (3 Steps)
```
1. Material Browser → Click "Aluminum"
2. Visualization Tab → Already selected!
3. Select properties → Generate Plot → Done!
```

### With Data View Modes (4 Steps)
```
1. Material Browser → Click "Copper"
2. Visualization Tab → Choose view mode:
   • "Active View (with Overrides)" ← shows modified data
   • "Original Data (no Overrides)" ← shows raw data
3. Select properties
4. Generate Plot
```

---

## 🔗 Linked Features

| Material Browser Tab | Visualization Feature | Link |
|---------------------|----------------------|------|
| **Material Selection** | Material List | ✅ Auto-selects |
| **Original Data** | "Original Data" mode | ✅ Same data |
| **Active View** | "Active View" mode | ✅ Same data |
| **Overrides** | View mode toggle | ✅ Respects overrides |
| **References** | Dashboard details | ✅ Shows ref IDs |

---

## 🎨 Visual Guide

```
┌─────────────────┐         ┌──────────────────┐
│ Material Browser│         │  Visualization   │
│                 │         │                  │
│ Click "Copper" ─┼────────→│ "Copper" ✓      │
│                 │  Syncs  │                  │
│ Original Data   ├────────→│ Mode: Original   │
│ Active View     ├────────→│ Mode: Active     │
│ References      ├────────→│ Dashboard: Refs  │
└─────────────────┘         └──────────────────┘
```

---

## 🔍 Console Output (When Working)

```python
# When you select material in browser:
[MainWindow] Syncing material 'Copper' to visualization tab
[VizTab] Selecting material: Copper
[VizTab] Material 'Copper' selected in visualization tab

# When you generate plot:
=== GENERATE PLOT CALLED ===
Selected materials: ['Copper']
Selected properties: ['density']
[VizTab] Fetching Copper with overrides=True
Plot generated successfully!
```

---

## 🐛 Troubleshooting

**Q: Material not auto-selecting?**
- Check console for sync messages
- Ensure material exists in database

**Q: Plot empty?**
- Check console for "Properties found: []"
- Try different properties

**Q: Overrides not showing?**
- Ensure "Active View (with Overrides)" selected
- Verify overrides exist in database

---

## 📁 Key Files

| File | What Changed |
|------|--------------|
| `gui/main_window.py` | Added 1 line to sync selection |
| `gui/views/visualization_tab.py` | Added view modes, refs, debugging |

---

## 📚 Full Documentation

- **VISUALIZATION_INTEGRATION.md** → Complete guide with diagrams
- **INTEGRATION_TEST_SUMMARY.md** → Testing checklist
- **VISUALIZATION_IMPLEMENTATION_SUMMARY.md** → Technical details

---

## ✅ Ready to Use!

```bash
python run_gui.py
```

**Try it now**:
1. Click any material in Material Browser
2. Switch to Visualization tab
3. It's already selected! ✨

---

**That's it! Fully integrated and ready to visualize!** 🎉
