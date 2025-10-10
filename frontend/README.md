# 📊 Input Configuration Manager

A simple web-based UI for managing scenario configurations for the AIH analysis system.

## 🚀 Getting Started

### Option 1: Direct File Access
1. Navigate to the `frontend` folder
2. Open `index.html` in your web browser
3. Start configuring your scenarios!

### Option 2: Simple HTTP Server (Recommended)
For better functionality and to avoid CORS issues:

```bash
# Navigate to the frontend directory
cd frontend

# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (if you have npm installed)
npx http-server

# Then open http://localhost:8000 in your browser
```

## 📋 Features

### ✨ Core Functionality
- **Scenario Management**: Select from existing scenarios (PG, Support, TA, CMO, Test) or create new ones
- **Form-based Input**: Easy-to-use forms for all configuration fields
- **Real-time Validation**: Input validation and helpful hints
- **Auto-save**: Automatically saves changes after 2 seconds of inactivity

### 📤 Import/Export
- **JSON Export**: Export complete configuration to JSON format
- **JSON Import**: Import existing configurations from JSON files
- **Copy to Clipboard**: Quick copy functionality for generated JSON
- **Download JSON**: Download configuration as a file

### ⌨️ Keyboard Shortcuts
- **Ctrl/Cmd + S**: Save current configuration
- **Ctrl/Cmd + E**: Export to JSON

## 📊 Configuration Fields

The UI collects the following information for each scenario:

### 📋 Basic Configuration
- **TML Filename**: ThoughtSpot TML file reference
- **Worksheet ID**: ThoughtSpot worksheet identifier
- **Date Column**: Primary date field for temporal analysis

### 📈 KPIs and Metrics
- **KPIs**: Key Performance Indicators description
- **Aggregations**: Important numbers and calculations

### 🎯 Analysis Configuration
- **Attributes**: Key dimensions for data slicing
- **Goal**: Primary objective of the analysis
- **User Context**: Detailed requirements and context

### 📄 Report Configuration
- **Report Format**: Desired structure of the final report

## 💾 Data Management

### Saving Configurations
1. Select a scenario from the dropdown
2. Fill in the form fields
3. Click "💾 Save Configuration" or use Ctrl/Cmd+S
4. Configuration is saved locally in the browser

### Exporting Data
1. After configuring scenarios, click "📤 Export JSON"
2. The complete configuration appears in JSON format
3. Use "📋 Copy to Clipboard" or "💾 Download JSON"
4. Save this JSON to your `backend/inputs.json` file

### Importing Data
1. Click "📥 Import JSON"
2. Select your `inputs.json` file
3. All scenarios will be loaded into the UI
4. Select any scenario to view/edit its configuration

## 🔧 Integration with Backend

To use the generated configuration with your analysis system:

1. **Export** your configuration using the UI
2. **Copy** the generated JSON
3. **Replace** the contents of `backend/inputs.json` with the exported data
4. **Run** your analysis with the updated configuration

## 📱 Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## 🎨 Responsive Design

The UI is fully responsive and works on:
- 💻 Desktop computers
- 📱 Tablets
- 📱 Mobile phones

## 🚀 Example Workflow

1. **Open** the UI in your browser
2. **Select** "Product Growth (PG)" scenario
3. **Review** the pre-loaded configuration
4. **Modify** fields as needed
5. **Save** the configuration
6. **Export** to JSON format
7. **Copy** the JSON and update your `backend/inputs.json`
8. **Run** your analysis system

## 📝 Notes

- All data is stored locally in your browser
- Use the import/export functionality to backup your configurations
- The UI includes sample data from your existing `inputs.json` file
- Missing fields are automatically filled with "NA" values

## 🛠️ Customization

To modify the UI:
- **HTML**: Edit `index.html` for structure changes
- **CSS**: Edit `styles.css` for styling modifications
- **JavaScript**: Edit `script.js` for functionality updates

## 🆘 Troubleshooting

**Issue**: Can't load the page  
**Solution**: Make sure you're using an HTTP server or try a different browser

**Issue**: Data not saving  
**Solution**: Check browser console for errors, ensure JavaScript is enabled

**Issue**: Import not working  
**Solution**: Ensure your JSON file is valid and follows the expected structure

## 📞 Support

If you encounter any issues:
1. Check the browser console for error messages
2. Verify your JSON structure matches the expected format
3. Try refreshing the page and starting over
