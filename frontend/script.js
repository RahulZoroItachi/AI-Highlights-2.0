// Complete data from inputs.json structure
let sampleData = {
    "pg": {
        "tml_filename": "NA",
        "liveboard_id": "",
        "worksheet_id": "9cfb299b-7378-48cb-ae20-a0bc5a82b223",
        "kpi": "The primary KPIs are M1, S0, and S1, which are different values within the 'Opportunity Stage' column. The KPIs are the count of opportunities and the total sum of 'Opportunity ACV'. ",
        "attributes": "The analysis should focus on slicing the data by 'Opportunity Type', 'Opportunity Owner Name', Opportunity Creator Name, Opportunity Creator Team,'Opportunity Owner Team', Opportunity Name.",
        "aggregations": "The most important numbers are the count of opportunities and the total sum of 'Opportunity ACV'.",
        "date_column": "Opportunity Created Date",
        "goal": "The goal is to understand how our early-stage pipeline is performing weekly across different teams. creators/owners and opportunity types, in order to identify high-performance areas and diagnose potential bottlenecks for targeted action.",
        "user_context": "The analysis should be across each Opportunity Stage. Always treat each opportunity stage as a separate entity. I want the performance by Opportunity Team, Opportunity Owner and Opportunity Type for each Opportunity stage. Do this analysis for the last week. Then do the analysis for the last 8 weeks. Then compare them too. Output I need:1. Last week performance for each Opp stage across the important attributes 2. Last 8 weeks performance for each Opp stage across the important attributes 3. How my current week compares to the last 8 weeks. I treat each opportunity stage as a separate entity. Do not mix the data across stages. For M1, use Opportunity Creator Name instead of Opportunity Owner Name. For S0 and S1, use Opportunity Owner Name. ACV for each stage is a measure of the format M1 Starting ACV etc. Opportunity Region Segment should alwas be set to 'emea commercial' and 'emea enterprise'. Add this filter in all the data fetch as I am interested only in EMEA region and not any other region. NOTE: When analysing the individual Opprotunity Owner or Creator for each stage, I want to know the names and ACV of the top accounts/opportunities for each owner for each stage. Listing the names of the top accounts that made the owner perform well.",
        "report_format": "The report should have 1. Executive summary that focuses on the last week and how it compares to the last to last week and the last 8 week average. 2. Detailed analysis of the last week across each Opp stage separately 3. How the last week compares to the last to last week 4. How last week compares to the last 8 weeks"
    },
    "support": {
        "tml_filename": "NA",
        "liveboard_id": "",
        "worksheet_id": "1abdd9fa-d207-440e-9906-4715dc81ac0b",
        "kpi": "The primary KPIs are NPS Support, NPS Overall, Rolling 90 days NPS",
        "attributes": "The analysis should focus on slicing the data by Case NPS Score Segment, Case Owner Name, Account Name, Case NPS Score, Case NPS Feedback comments",
        "aggregations": "The most important numbers are the count of opportunities and the total sum of 'Opportunity ACV'.",
        "date_column": "Daily Survey Completion Date Time",
        "goal": "The goal is to understand how the NPS score is for the overall product as well as for the support function. To identify patterns in Accounts and Owners to give a good experience to the users",
        "user_context": "The analysis should be across Account Name, Case Owner name for the last 7 days. I want the overall performance across Promoters, Detractors and Passives. For Detractors and Passives, I want to know by Case Owner and Account name. I also want to know the comments for these. Do this analysis for the last week. Then do the analysis for the last to last week. Then do the analysis for the last 8 week average. Then compare them. The most important tab is \"Customer Health\" and the most important table in that is \"NPS Comment Details\". Output I need: 1) Last week performance for each NPS segment, primarily focusing on Detractors and Promoters across the important attributes 2) Last to last weeks performance for each NPS segment, primarily focusing on Detractors and Promoters across the important attributes 3) Last 8 week average performance for each NPS segment, primarily focusing on Detractors and Promoters across the important attributes 4) How my current week compares to the last 8 weeks",
        "report_format": "The report should have 1. Executive summary that focuses on the last week and how it compares to the last to last week and the last 8 week average. 2. Detailed analysis of the last week across important attributes3. How the last week compares to the last to last week 4. How last week compares to the last 8 weeks"
    },
    "ta": {
        "tml_filename": "NA",
        "liveboard_id": "",
        "worksheet_id": "ta-worksheet-id",
        "kpi": "Talent acquisition KPIs: Time-to-Hire, Offer Acceptance Rate",
        "attributes": "Role, Department, Recruiter, Region",
        "aggregations": "AVG(Time to Hire), COUNT(Offers), RATE(Acceptance)",
        "date_column": "Application Created Date",
        "goal": "Optimize hiring funnel and identify bottlenecks",
        "user_context": "Monthly trend by department and role seniority",
        "report_format": "Executive summary with hiring metrics, funnel analysis by department and role, time-to-hire trends, and recommendations for improving recruitment efficiency."
    },
    "cmo": {
        "tml_filename": "NA",
        "liveboard_id": "",
        "worksheet_id": "088155b8-4dc2-446b-98b9-a24e43a73860",
        "kpi": "The primary KPIs M1, S0 and S1 quarterly. These are the values within the 'Creation Target Creation Metric' column. The measures are 1. 'Creation Achieved' - This gives the count of opportunities. 2.  'Creation ACV Achieved'- This gives the sum of the ACV of the opportunities. These 2 measures when combined with the 'Creation Target Creation Metric' will give the KPIs for each KPI. For each 'Creation Target Creation Metric', there are 2 KPIs. The target measures are 1. 'Creation ACV Target' - This gives the target ACV for each KPI. 2. 'Creation Target' - This gives the target count for each KPI. Apply 'Creation Target Opportunity Type' = existing customer expansion,'Creation Target Opportunity Type'=  new customer and [Opportunity Deployment] != 'mode' for all KPIs without fail",
        "attributes": " Creation Target Region Segment, Creation Target Opportunity Type, Creation Target Opportunity Source",
        "aggregations": "ACV and Cunt and separate measures and hence no aggregation is needed",
        "date_column": "Creation Month",
        "goal": "The goal is to understand how the KPIs are trending towards the target. Which Geo, Source and Segment are lagging behind and needs attention",
        "user_context": "The analysis should be performed only on 'this quarter'. For each KPI, I want to know how it is trending towards the target. I want to treat the count and ACV of each of the 'Creation Target Creation Metric' as a separate entity while fetching data and analysing. THey need to be treated as separate KPIs. There is a formula to compute 'pts to pace' is a measure that gives a quantifiable number on how the KPI with the filters is trending towards the target with respect to the days in the quarter. Computation of points to pace : ' I want you to take the achieved number and divide it by the target number. multiply this result by 100. Have upto 1 decimal place.  Subtract this result and  74.7 (result_a - 74.7). This final number is the points to pace.'. This needs to be calculated once the data is fetched for each KPI across each attribute. This tells if we are ahead or behind the target with respect to the time progressed. I analyse first by Creation Target Region Segment (Geos). What are the Geos whose points to pace are the most negative. ALWAYS Within each Geos, I will look for the Source that are not performing well. Within the sources i will look for Opportunity Type. I ALWAYS look at the information in this hierarchy. Any other hierarchy should not be followed. This is a marketing funnel with each KPI being stages in a funnel. I want the analysis separatly for the count and ACV KPIs for each 'Creation Target Creation Metric'. In the Liveboard, the 'Creation to Targets' is the most important tab. It has pivot tables for each KPI across the important attributes as mentioned above. Critical: As you prepare the data fetch plan first and then run the analysis, you will not know which are the worst performing regions to get the Opportunity Source. Hence, get the opportunity Source for all the regions separately in the fetch plan. So that you can use it to analyse it. Do the same for Opportunity Type, as you will not know the worst performing Opportunity Source. Output I need: 1. Performance of each KPI as per the hierarchy mentioned for the target. Give as much information in terms of numbers as you have. Present all the relevant numbers in an easy to understand format. For each KPI, give me the analysis as per the hierarchy. In the analysis, mention the points to pace for each section of the analysis.  Very Important: THe Quarter starts in the month of August. To fetch data for this quarter, adding Creation Month = 'this quarter' to the prompt is enough, no need to mention the months",
        "report_format": "The report should have 1. Executive summary 2. Detailed analysis of M1 (Count and ACV) as per the hierarchy 3. Detailed analysis of S0 (Count and ACV) as per the hierarchy 4. Detailed analysis of S1 (Count and ACV) as per the hierarchy. "
    },
    "test": {
        "tml_filename": "NA",
        "liveboard_id": "",
        "worksheet_id": "test-worksheet-id",
        "kpi": "unique count [Case Number], unique count [Case ID], average [Case Full Resolution Time Minutes], [formula_Total NPS Score] / count [Survey Invitation Name], [formula_CSAT Positive] / ([formula_CSAT Negative] + [formula_CSAT Positive]), unique count [Cluster Name], unique count [Account Name], average [Case Customer Wait Time Minutes]",
        "attributes": "Case Priority, Case Owner Name, Account Name, Case Closed Time, Case Created Time",
        "aggregations": "COUNT(Records), SUM(Value)",
        "date_column": "Creation Month",
        "goal": "Test scenario for metadata extraction",
        "user_context": "Test analysis requirements",
        "report_format": "Test report format"
    }
};

let currentData = {};
let currentScenario = null;

// Load scenario data
function loadScenario() {
    const scenarioSelect = document.getElementById('scenario');
    const selectedScenario = scenarioSelect.value;
    const form = document.getElementById('input-form');
    const output = document.getElementById('output');
    
    if (!selectedScenario) {
        form.style.display = 'none';
        output.style.display = 'none';
        return;
    }
    
    // Show form
    form.style.display = 'block';
    output.style.display = 'none';
    
    // Load data for selected scenario
    const data = sampleData[selectedScenario] || {};
    
    // Populate form fields
    document.getElementById('liveboard_id').value = data.liveboard_id || '';
    document.getElementById('worksheet_id').value = data.worksheet_id || '';
    document.getElementById('kpi').value = data.kpi || '';
    document.getElementById('attributes').value = data.attributes || '';
    document.getElementById('aggregations').value = data.aggregations || '';
    document.getElementById('date_column').value = data.date_column || '';
    document.getElementById('goal').value = data.goal || '';
    document.getElementById('user_context').value = data.user_context || '';
    document.getElementById('report_format').value = data.report_format || '';
    
    // Store current data
    currentData = { ...data };
    
    showMessage(`Loaded configuration for ${selectedScenario.toUpperCase()} scenario`, 'success');
}

// Create new scenario
function createNewScenario() {
    const scenarioName = prompt('Enter new scenario name (lowercase, no spaces):');
    if (!scenarioName) return;
    
    // Validate scenario name
    if (!/^[a-z_]+$/.test(scenarioName)) {
        showMessage('Scenario name must be lowercase letters and underscores only', 'error');
        return;
    }
    
    // Check if scenario already exists
    if (sampleData[scenarioName]) {
        showMessage('Scenario already exists. Please choose a different name.', 'error');
        return;
    }
    
    // Add to select options immediately
    const scenarioSelect = document.getElementById('scenario');
    const option = document.createElement('option');
    option.value = scenarioName;
    option.textContent = scenarioName.charAt(0).toUpperCase() + scenarioName.slice(1);
    scenarioSelect.appendChild(option);
    
    // Select the new scenario
    scenarioSelect.value = scenarioName;
    
    // Clear form and show it
    clearForm();
    document.getElementById('input-form').style.display = 'block';
    
    // Set the scenario name in the form state
    currentScenario = scenarioName;
    
    showMessage(`✅ New scenario "${scenarioName}" created! Enter the Liveboard ID and click "Auto Fill Configuration" to extract inputs automatically, or fill in the fields manually.`, 'success');
}

// Stream scenario creation progress
function startScenarioCreationProgressStreaming(sessionId, scenarioName) {
    console.log(`🔄 Starting scenario creation progress stream for session: ${sessionId}`);
    
    const eventSource = new EventSource(`http://localhost:5000/api/create-scenario-progress/${sessionId}`);
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 Scenario creation progress message received:', data);
            
            if (data.output) {
                console.log(`📋 Progress: ${data.output}`);
                showMessage(`📋 ${data.output}`, 'info');
                
            } else if (data.complete) {
                console.log('✅ Scenario creation completed');
                showMessage('✅ Scenario creation completed successfully!', 'success');
                eventSource.close();
                
                // Load the newly created scenario data
                loadScenarioFromCreation(scenarioName, data.inputs_data);
                
                showMessage(`🎉 New scenario "${scenarioName}" created and populated with extracted inputs!`, 'success');
                
            } else if (data.error) {
                console.error('❌ Scenario creation error:', data.message);
                showMessage(`❌ Error: ${data.message}`, 'error');
                eventSource.close();
                
                // Remove the optimistically added option on error
                const scenarioSelect = document.getElementById('scenario');
                const option = scenarioSelect.querySelector(`option[value="${scenarioName}"]`);
                if (option) {
                    option.remove();
                }
                
            } else if (data.heartbeat) {
                console.log('💓 Heartbeat received');
            }
            
        } catch (parseError) {
            console.error('❌ Error parsing scenario creation progress message:', parseError);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('❌ Scenario creation progress stream error:', event);
        showMessage('❌ Connection error during scenario creation', 'error');
        eventSource.close();
    };
    
    // Store reference for cleanup if needed
    window.currentScenarioCreationStream = eventSource;
}

// Load scenario data from creation result
function loadScenarioFromCreation(scenarioName, inputsData) {
    if (inputsData) {
        // Update local sample data with the extracted inputs
        sampleData[scenarioName] = inputsData;
        
        // Populate form fields with the extracted data
        document.getElementById('liveboard_id').value = inputsData.liveboard_id || '';
        document.getElementById('worksheet_id').value = inputsData.worksheet_id || '';
        document.getElementById('kpi').value = inputsData.kpi || '';
        document.getElementById('attributes').value = inputsData.attributes || '';
        document.getElementById('aggregations').value = inputsData.aggregations || '';
        document.getElementById('date_column').value = inputsData.date_column || '';
        document.getElementById('goal').value = inputsData.goal || '';
        document.getElementById('user_context').value = inputsData.user_context || '';
        document.getElementById('report_format').value = inputsData.report_format || '';
        
        console.log('✅ Loaded extracted inputs into form for scenario:', scenarioName);
    }
    
    // Restore Auto Fill button state
    const button = document.querySelector('.auto-fill-btn');
    if (button) {
        button.disabled = false;
        button.innerHTML = '🤖 Auto Fill Configuration';
    }
}

// Save configuration
function saveConfiguration() {
    const scenarioSelect = document.getElementById('scenario');
    const selectedScenario = scenarioSelect.value;
    
    if (!selectedScenario) {
        showMessage('Please select a scenario first', 'error');
        return;
    }
    
    // Collect form data
    const formData = {
        tml_filename: 'NA', // Always set to NA as per requirement
        liveboard_id: document.getElementById('liveboard_id').value || 'NA',
        worksheet_id: document.getElementById('worksheet_id').value || 'NA',
        kpi: document.getElementById('kpi').value || 'NA',
        attributes: document.getElementById('attributes').value || 'NA',
        aggregations: document.getElementById('aggregations').value || 'NA',
        date_column: document.getElementById('date_column').value || 'NA',
        goal: document.getElementById('goal').value || 'NA',
        user_context: document.getElementById('user_context').value || 'NA',
        report_format: document.getElementById('report_format').value || 'NA'
    };
    
    // Update local sample data
    sampleData[selectedScenario] = formData;
    currentData = { ...formData };
    
    // Save to backend via API
    saveToBackend(selectedScenario, formData);
}

// Auto Fill Configuration function
async function autoFillConfiguration() {
    // Get the input values
    const liveboardId = document.getElementById('liveboard_id').value.trim();
    const worksheetId = document.getElementById('worksheet_id').value.trim();
    
    // Get current scenario name
    const scenarioSelect = document.getElementById('scenario');
    const currentScenarioName = scenarioSelect.value;
    
    if (!currentScenarioName) {
        showMessage('❌ Please select or create a scenario first', 'error');
        return;
    }
    
    // Validate inputs - only Liveboard ID is mandatory
    if (!liveboardId) {
        showMessage('❌ Please enter a Liveboard ID before auto-filling configuration', 'error');
        document.getElementById('liveboard_id').focus();
        return;
    }
    
    // Basic format validation for Liveboard ID (mandatory)
    const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    
    if (!uuidPattern.test(liveboardId)) {
        showMessage('⚠️ Liveboard ID format appears invalid. Please check and try again.', 'warning');
        document.getElementById('liveboard_id').focus();
        return;
    }
    
    // Validate Worksheet ID only if provided (optional)
    if (worksheetId && !uuidPattern.test(worksheetId)) {
        showMessage('⚠️ Worksheet ID format appears invalid. Please check and try again.', 'warning');
        document.getElementById('worksheet_id').focus();
        return;
    }
    
    // Show processing state and progress container
    const button = document.querySelector('.auto-fill-btn');
    const originalText = button.innerHTML;
    const progressContainer = document.getElementById('auto-fill-progress');
    const progressLog = document.getElementById('auto-fill-log');
    
    button.disabled = true;
    button.innerHTML = '⏳ Processing...';
    progressContainer.style.display = 'block';
    progressLog.innerHTML = ''; // Clear previous logs
    
    // Add initial message to log
    addToAutoFillLog('🚀 Starting input population from liveboard...');
    
    try {
        showMessage('🚀 Starting input population from liveboard...', 'info');
        
        // Call the backend API to trigger input population using the create-scenario endpoint
        const response = await fetch('http://localhost:5000/api/create-scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scenario_name: currentScenarioName,
                liveboard_id: liveboardId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('✅ Input population started successfully!', 'success');
            addToAutoFillLog('✅ Input population started successfully!');
            
            // Start streaming progress to the auto-fill log
            startAutoFillProgressStreaming(result.session_id, currentScenarioName);
            
        } else {
            throw new Error(result.error || 'Unknown error occurred');
        }
        
    } catch (error) {
        console.error('❌ Error starting input population:', error);
        showMessage(`❌ Error: ${error.message}`, 'error');
        addToAutoFillLog(`❌ Error: ${error.message}`);
        
        // Restore button state
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Add message to auto-fill log with color coding
function addToAutoFillLog(message) {
    const progressLog = document.getElementById('auto-fill-log');
    const logEntry = document.createElement('div');
    logEntry.className = 'progress-line';
    
    // Add color coding based on message content
    if (message.includes('❌') || message.includes('Error')) {
        logEntry.classList.add('error');
    } else if (message.includes('✅') || message.includes('completed')) {
        logEntry.classList.add('success');
    } else if (message.includes('⚠️') || message.includes('Warning')) {
        logEntry.classList.add('warning');
    } else if (message.includes('🔍') || message.includes('Processing') || message.includes('Analyzing')) {
        logEntry.classList.add('info');
    } else if (message.includes('📊') || message.includes('KPIs') || message.includes('identified')) {
        logEntry.classList.add('data');
    } else if (message.includes('📋') || message.includes('Creating') || message.includes('Extracting')) {
        logEntry.classList.add('process');
    }
    
    logEntry.textContent = message;
    progressLog.appendChild(logEntry);
    
    // Auto-scroll to bottom
    progressLog.scrollTop = progressLog.scrollHeight;
}

// Stream auto-fill progress
function startAutoFillProgressStreaming(sessionId, scenarioName) {
    console.log(`🔄 Starting auto-fill progress stream for session: ${sessionId}`);
    
    const eventSource = new EventSource(`http://localhost:5000/api/create-scenario-progress/${sessionId}`);
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 Auto-fill progress message received:', data);
            
            if (data.output) {
                console.log(`📋 Progress: ${data.output}`);
                addToAutoFillLog(data.output);
                
            } else if (data.complete) {
                console.log('✅ Auto-fill completed');
                addToAutoFillLog('✅ Auto-fill completed successfully!');
                eventSource.close();
                
                // Load the newly created scenario data
                loadScenarioFromCreation(scenarioName, data.inputs_data);
                
                showMessage(`🎉 Scenario "${scenarioName}" populated with extracted inputs!`, 'success');
                addToAutoFillLog(`🎉 Scenario "${scenarioName}" populated with extracted inputs!`);
                
            } else if (data.error) {
                console.error('❌ Auto-fill error:', data.message);
                addToAutoFillLog(`❌ Error: ${data.message}`);
                eventSource.close();
                
                // Restore button state
                const button = document.querySelector('.auto-fill-btn');
                if (button) {
                    button.disabled = false;
                    button.innerHTML = '🤖 Auto Fill Configuration';
                }
                
            } else if (data.heartbeat) {
                console.log('💓 Heartbeat received');
                addToAutoFillLog('⏳ Processing... (system is working)');
            }
            
        } catch (parseError) {
            console.error('❌ Error parsing auto-fill progress message:', parseError);
            addToAutoFillLog('❌ Error parsing progress message');
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('❌ Auto-fill progress stream error:', event);
        addToAutoFillLog('❌ Connection error during auto-fill process');
        eventSource.close();
    };
    
    // Store reference for cleanup if needed
    window.currentAutoFillStream = eventSource;
}

// Clear auto-fill log
function clearAutoFillLog() {
    const progressLog = document.getElementById('auto-fill-log');
    progressLog.innerHTML = '';
}

// Stream input population progress
function startPopulationProgressStreaming(sessionId) {
    console.log(`🔄 Starting progress stream for session: ${sessionId}`);
    
    const eventSource = new EventSource(`http://localhost:5000/api/populate-progress/${sessionId}`);
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 Progress message received:', data);
            
            if (data.output) {
                console.log(`📋 Progress: ${data.output}`);
                showMessage(`📋 ${data.output}`, 'info');
                
            } else if (data.complete) {
                console.log('✅ Input population completed');
                showMessage('✅ Input population completed successfully!', 'success');
                eventSource.close();
                
                // Restore button state
                const button = document.querySelector('.auto-fill-btn');
                button.disabled = false;
                button.innerHTML = '🤖 Auto Fill Configuration';
                
                // Show completion message
                showMessage('🎉 Input extraction completed! Generated inputs are ready.', 'success');
                
            } else if (data.error) {
                console.error('❌ Input population error:', data.message);
                showMessage(`❌ Error: ${data.message}`, 'error');
                eventSource.close();
                
                // Restore button state
                const button = document.querySelector('.auto-fill-btn');
                button.disabled = false;
                button.innerHTML = '🤖 Auto Fill Configuration';
                
            } else if (data.heartbeat) {
                console.log('💓 Heartbeat received');
            }
            
        } catch (parseError) {
            console.error('❌ Error parsing progress message:', parseError);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('❌ Progress stream error:', event);
        showMessage('❌ Connection error during input population', 'error');
        eventSource.close();
        
        // Restore button state
        const button = document.querySelector('.auto-fill-btn');
        button.disabled = false;
        button.innerHTML = '🤖 Auto Fill Configuration';
    };
    
    // Store reference for cleanup if needed
    window.currentPopulationStream = eventSource;
}

// Save to backend API
async function saveToBackend(scenario, data) {
    try {
        // Show loading state
        const saveButton = document.querySelector('button[onclick="saveConfiguration()"]');
        const originalText = saveButton.textContent;
        saveButton.textContent = '💾 Saving...';
        saveButton.disabled = true;
        
        const response = await fetch('http://localhost:5000/api/inputs/scenario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scenario: scenario,
                data: data
            })
        });
        
        const result = await response.json();
        
        // Restore button state
        saveButton.textContent = originalText;
        saveButton.disabled = false;
        
        if (result.success) {
            showMessage(`✅ Configuration saved for ${scenario.toUpperCase()} - inputs.json updated!`, 'success');
            
            // Refresh scenarios from API to pick up any new ones
            await loadScenariosFromAPI();
            updateScenarioSelector();
        } else {
            // Fallback to local storage if API fails
            console.warn('API save failed, using local storage:', result.error);
            showMessage(`⚠️ Saved locally (API unavailable): ${result.error}`, 'warning');
        }
        
    } catch (error) {
        // Restore button state
        const saveButton = document.querySelector('button[onclick="saveConfiguration()"]');
        saveButton.textContent = '💾 Save Configuration';
        saveButton.disabled = false;
        
        console.warn('API not available, saving locally:', error);
        showMessage(`💾 Saved locally - Start API server to save to inputs.json`, 'warning');
    }
}

// Export configuration
function exportConfiguration() {
    const scenarioSelect = document.getElementById('scenario');
    const selectedScenario = scenarioSelect.value;
    
    if (!selectedScenario) {
        showMessage('Please select a scenario first', 'error');
        return;
    }
    
    // Save current form data first
    saveConfiguration();
    
    // Generate complete configuration including current scenario
    const exportData = { ...sampleData };
    
    // Show output
    const output = document.getElementById('output');
    const jsonOutput = document.getElementById('json-output');
    
    jsonOutput.textContent = JSON.stringify(exportData, null, 2);
    output.style.display = 'block';
    
    // Scroll to output
    output.scrollIntoView({ behavior: 'smooth' });
    
    showMessage('Configuration exported to JSON format', 'success');
}

// Import configuration
function importConfiguration() {
    const fileInput = document.getElementById('file-input');
    fileInput.click();
}

// Handle file import
function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const importedData = JSON.parse(e.target.result);
            
            // Validate structure
            if (typeof importedData === 'object' && importedData !== null) {
                // Merge with existing data
                Object.assign(sampleData, importedData);
                
                // Update scenario selector
                updateScenarioSelector();
                
                showMessage('Configuration imported successfully', 'success');
            } else {
                throw new Error('Invalid JSON structure');
            }
        } catch (error) {
            showMessage('Error importing configuration: ' + error.message, 'error');
        }
    };
    reader.readAsText(file);
    
    // Reset file input
    event.target.value = '';
}

// Load scenarios from API
async function loadScenariosFromAPI() {
    try {
        const response = await fetch('http://localhost:5000/api/inputs');
        const result = await response.json();
        
        if (result.success && result.data) {
            // Update sampleData with API data
            Object.keys(result.data).forEach(scenario => {
                sampleData[scenario] = result.data[scenario];
            });
            console.log('✅ Loaded scenarios from API:', Object.keys(result.data));
            return true;
        } else {
            console.warn('⚠️ API returned no data, using local sample data');
            return false;
        }
    } catch (error) {
        console.warn('⚠️ Could not load from API, using local sample data:', error.message);
        return false;
    }
}

// Refresh scenarios from API
async function refreshScenarios() {
    const refreshButton = document.getElementById('refresh-scenarios-btn');
    const originalText = refreshButton.textContent;
    
    try {
        // Show loading state
        refreshButton.textContent = '🔄';
        refreshButton.disabled = true;
        
        // Load fresh data from API
        const success = await loadScenariosFromAPI();
        
        // Update dropdown
        updateScenarioSelector();
        
        if (success) {
            showMessage('✅ Scenarios refreshed from inputs.json', 'success');
        } else {
            showMessage('⚠️ Could not connect to API - using cached data', 'warning');
        }
        
    } finally {
        // Restore button state
        refreshButton.textContent = originalText;
        refreshButton.disabled = false;
    }
}

// Update scenario selector with imported data
function updateScenarioSelector() {
    const scenarioSelect = document.getElementById('scenario');
    const currentValue = scenarioSelect.value;
    
    // Clear existing options except the first one
    scenarioSelect.innerHTML = '<option value="">Select a scenario...</option>';
    
    // Add scenarios from data (now loaded from API or local fallback)
    const scenarioNames = {
        'pg': 'Product Growth (PG)',
        'support': 'Support',
        'ta': 'Talent Acquisition (TA)',
        'cmo': 'CMO',
        'test': 'Test'
    };
    
    Object.keys(sampleData).forEach(scenario => {
        if (scenario !== 'stg') { // Skip staging data
            const option = document.createElement('option');
            option.value = scenario;
            option.textContent = scenarioNames[scenario] || scenario.charAt(0).toUpperCase() + scenario.slice(1);
            scenarioSelect.appendChild(option);
        }
    });
    
    // Restore selection if it still exists
    if (currentValue && sampleData[currentValue]) {
        scenarioSelect.value = currentValue;
    }
}

// Clear form
function clearForm() {
    const inputs = document.querySelectorAll('#input-form input, #input-form textarea');
    inputs.forEach(input => input.value = '');
    
    document.getElementById('output').style.display = 'none';
    
    showMessage('Form cleared', 'success');
}

// Copy to clipboard
function copyToClipboard() {
    const jsonOutput = document.getElementById('json-output');
    const textArea = document.createElement('textarea');
    textArea.value = jsonOutput.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    showMessage('Configuration copied to clipboard', 'success');
}

// Show message
function showMessage(message, type = 'success') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Insert after header
    const header = document.querySelector('header');
    header.insertAdjacentElement('afterend', messageDiv);
    
    // Remove message after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Download JSON file
function downloadJSON() {
    const jsonOutput = document.getElementById('json-output');
    const data = jsonOutput.textContent;
    
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'inputs_config.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
    showMessage('Configuration downloaded as JSON file', 'success');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    // Load scenarios from API first
    await loadScenariosFromAPI();
    
    // Then update both dropdowns
    updateScenarioSelector();
    updateAnalysisScenarioSelector();
    
    showMessage('Welcome! Select a scenario to begin configuration.', 'success');
});

// Tab switching functionality
async function switchTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    const activeButton = document.querySelector(`[onclick="switchTab('${tabName}')"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
    
    // Refresh data when switching tabs
    if (tabName === 'analysis') {
        await refreshAnalysisScenarios();
    } else if (tabName === 'configuration') {
        await refreshScenarios();
    }
}

// Update analysis scenario selector
function updateAnalysisScenarioSelector() {
    const scenarioSelect = document.getElementById('analysis-scenario');
    const currentValue = scenarioSelect.value;
    
    // Clear existing options except the first one
    scenarioSelect.innerHTML = '<option value="">Choose a scenario to analyze...</option>';
    
    // Add scenarios from data (loaded from API or local fallback)
    const scenarioNames = {
        'pg': 'Product Growth (PG)',
        'support': 'Support',
        'ta': 'Talent Acquisition (TA)',
        'cmo': 'CMO',
        'test': 'Test'
    };
    
    Object.keys(sampleData).forEach(scenario => {
        if (scenario !== 'stg') { // Skip staging data
            const option = document.createElement('option');
            option.value = scenario;
            option.textContent = scenarioNames[scenario] || scenario.charAt(0).toUpperCase() + scenario.slice(1);
            scenarioSelect.appendChild(option);
        }
    });
    
    // Restore selection if it still exists
    if (currentValue && sampleData[currentValue]) {
        scenarioSelect.value = currentValue;
        loadAnalysisScenario(); // Load the scenario data
    }
}

// Load analysis scenario data
async function loadAnalysisScenario() {
    const scenarioSelect = document.getElementById('analysis-scenario');
    const selectedScenario = scenarioSelect.value;
    const analysisContent = document.getElementById('analysis-content');
    
    if (!selectedScenario) {
        analysisContent.style.display = 'none';
        return;
    }
    
    // Show analysis content
    analysisContent.style.display = 'block';
    
    // Load available versions for this scenario
    await updateVersionDropdowns(selectedScenario);
    
    // Load scenario data
    const data = sampleData[selectedScenario] || {};
    
    // Populate configuration display
    document.getElementById('config-worksheet-id').textContent = data.worksheet_id || 'Not specified';
    document.getElementById('config-date-column').textContent = data.date_column || 'Not specified';
    document.getElementById('config-kpi').textContent = data.kpi || 'Not specified';
    document.getElementById('config-attributes').textContent = data.attributes || 'Not specified';
    document.getElementById('config-goal').textContent = data.goal || 'Not specified';
    document.getElementById('config-user-context').textContent = data.user_context || 'Not specified';
    
    showMessage(`Loaded configuration for ${selectedScenario.toUpperCase()} scenario`, 'success');
}

// Update version dropdowns based on available versions for scenario
async function updateVersionDropdowns(scenario) {
    try {
        const response = await fetch(`http://localhost:5000/api/versions/${scenario}`);
        const result = await response.json();
        
        if (result.success && result.versions) {
            const versions = result.versions;
            
            // Update Load Previous Plan dropdown
            const planSelect = document.getElementById('load-previous-plan');
            const currentPlan = planSelect.value;
            planSelect.innerHTML = '<option value="">Generate New Plan</option>';
            versions.plans.forEach(version => {
                const option = document.createElement('option');
                option.value = version;
                option.textContent = `Version ${version}`;
                planSelect.appendChild(option);
            });
            if (currentPlan && versions.plans.includes(parseInt(currentPlan))) {
                planSelect.value = currentPlan;
            }
            
            // Update Load Previous Data dropdown
            const dataSelect = document.getElementById('load-previous-data');
            const currentData = dataSelect.value;
            dataSelect.innerHTML = '<option value="">Fetch Fresh Data</option>';
            versions.data.forEach(version => {
                const option = document.createElement('option');
                option.value = version;
                option.textContent = `Version ${version}`;
                dataSelect.appendChild(option);
            });
            if (currentData && versions.data.includes(parseInt(currentData))) {
                dataSelect.value = currentData;
            }
            
            // Update Report Analysis Version dropdown
            const analysisSelect = document.getElementById('report-analysis-version');
            const currentAnalysis = analysisSelect.value;
            analysisSelect.innerHTML = '<option value="">Run Full Analysis</option>';
            versions.analysis.forEach(version => {
                const option = document.createElement('option');
                option.value = version;
                option.textContent = `Version ${version}`;
                analysisSelect.appendChild(option);
            });
            if (currentAnalysis && versions.analysis.includes(parseInt(currentAnalysis))) {
                analysisSelect.value = currentAnalysis;
            }
            
            console.log(`✅ Updated version dropdowns for ${scenario}:`, versions);
        } else {
            console.warn(`⚠️ Could not load versions for ${scenario}:`, result.error);
            // Reset to default options
            resetVersionDropdowns();
        }
    } catch (error) {
        console.error(`❌ Error loading versions for ${scenario}:`, error);
        resetVersionDropdowns();
    }
}

// Reset version dropdowns to default state
function resetVersionDropdowns() {
    const planSelect = document.getElementById('load-previous-plan');
    const dataSelect = document.getElementById('load-previous-data');
    const analysisSelect = document.getElementById('report-analysis-version');
    
    planSelect.innerHTML = '<option value="">Generate New Plan</option>';
    dataSelect.innerHTML = '<option value="">Fetch Fresh Data</option>';
    analysisSelect.innerHTML = '<option value="">Run Full Analysis</option>';
}

// Refresh analysis scenarios
async function refreshAnalysisScenarios() {
    const refreshButton = document.getElementById('refresh-analysis-scenarios-btn');
    const originalText = refreshButton.textContent;
    
    try {
        // Show loading state
        refreshButton.textContent = '🔄';
        refreshButton.disabled = true;
        
        // Load fresh data from API
        const success = await loadScenariosFromAPI();
        
        // Update dropdown
        updateAnalysisScenarioSelector();
        
        if (success) {
            showMessage('✅ Analysis scenarios refreshed from inputs.json', 'success');
        } else {
            showMessage('⚠️ Could not connect to API - using cached data', 'warning');
        }
        
    } finally {
        // Restore button state
        refreshButton.textContent = originalText;
        refreshButton.disabled = false;
    }
}

// Global variables for analysis session management
let currentAnalysisSession = null;
let progressEventSource = null;

// Run analysis function
async function runAnalysis() {
    const selectedScenario = document.getElementById('analysis-scenario').value;
    
    if (!selectedScenario) {
        showMessage('Please select a scenario first', 'error');
        return;
    }
    
    // Get analysis configuration
    const config = {
        scenario: selectedScenario,
        llm_provider: document.getElementById('llm-provider').value,
        load_previous_plan: document.getElementById('load-previous-plan').value || null,
        load_previous_data: document.getElementById('load-previous-data').value || null,
        report_analysis_version: document.getElementById('report-analysis-version').value || null
    };
    
    try {
        // Update UI to show running state
        const runButton = document.getElementById('run-analysis-btn');
        const stopButton = document.getElementById('stop-analysis-btn');
        const statusDisplay = document.getElementById('analysis-status');
        const statusContent = document.getElementById('status-content');
        const progressOutput = document.getElementById('progress-output');
        const progressLog = document.getElementById('progress-log');
        
        // Show status section and progress output
        statusDisplay.style.display = 'block';
        progressOutput.style.display = 'block';
        
        // Update button states
        runButton.style.display = 'none';
        stopButton.style.display = 'inline-flex';
        
        // Clear previous progress
        progressLog.innerHTML = '';
        
        // Show initial status
        statusContent.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 20px; height: 20px; border: 2px solid #10b981; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <span>Starting analysis for <strong>${selectedScenario.toUpperCase()}</strong>...</span>
            </div>
            <div style="margin-top: 15px; font-size: 13px; color: #6b7280;">
                <div>• LLM Provider: ${config.llm_provider}</div>
                <div>• Previous Plan: ${config.load_previous_plan || 'Generate New'}</div>
                <div>• Previous Data: ${config.load_previous_data || 'Fetch Fresh'}</div>
                <div>• Analysis Version: ${config.report_analysis_version || 'Run Full Analysis'}</div>
            </div>
        `;
        
        // Add spinning animation CSS if not exists
        if (!document.querySelector('#spin-animation')) {
            const style = document.createElement('style');
            style.id = 'spin-animation';
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Start analysis via API
        console.log('🚀 Starting analysis with config:', config);
        const response = await fetch('http://localhost:5000/api/analysis/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        console.log('📡 API response status:', response.status);
        const result = await response.json();
        console.log('📊 API response data:', result);
        
        if (result.success) {
            currentAnalysisSession = result.session_id;
            console.log('✅ Analysis session started:', currentAnalysisSession);
            showMessage(`🚀 Analysis started for ${selectedScenario.toUpperCase()} scenario`, 'success');
            
            // Start listening for progress updates
            startProgressStreaming(result.session_id);
            
        } else {
            throw new Error(result.error || 'Failed to start analysis');
        }
        
    } catch (error) {
        console.error('Error starting analysis:', error);
        showMessage(`❌ Failed to start analysis: ${error.message}`, 'error');
        resetAnalysisUI();
    }
}

// Start progress streaming
function startProgressStreaming(sessionId) {
    console.log('🔧 Starting progress streaming for session:', sessionId);
    
    // Close any existing connection
    if (progressEventSource) {
        progressEventSource.close();
    }
    
    // Create new EventSource connection
    const streamUrl = `http://localhost:5000/api/analysis/progress/${sessionId}`;
    console.log('🔧 Connecting to stream URL:', streamUrl);
    
    progressEventSource = new EventSource(streamUrl);
    
    const progressLog = document.getElementById('progress-log');
    const statusContent = document.getElementById('status-content');
    
    progressEventSource.onopen = function(event) {
        console.log('✅ Progress stream connected', event);
    };
    
    progressEventSource.onmessage = function(event) {
        console.log('📨 Received message:', event.data);
        try {
            const data = JSON.parse(event.data);
            console.log('📊 Parsed data:', data);
            
            switch (data.type) {
                case 'output':
                    // Add new progress line
                    const line = document.createElement('div');
                    line.className = 'progress-line';
                    
                    // Color code based on content
                    const message = data.message;
                    if (message.includes('❌') || message.includes('ERROR') || message.includes('Failed')) {
                        line.classList.add('error');
                    } else if (message.includes('✅') || message.includes('SUCCESS') || message.includes('Completed')) {
                        line.classList.add('success');
                    } else if (message.includes('⚠️') || message.includes('WARNING')) {
                        line.classList.add('warning');
                    } else if (message.includes('🔍') || message.includes('📊') || message.includes('📋')) {
                        line.classList.add('info');
                    }
                    
                    line.textContent = message;
                    progressLog.appendChild(line);
                    
                    // Auto-scroll to bottom
                    progressLog.scrollTop = progressLog.scrollHeight;
                    break;
                    
                case 'complete':
                    console.log('✅ Analysis completed');
                    statusContent.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="color: #10b981; font-size: 20px;">✅</div>
                            <span style="color: #10b981; font-weight: 600;">${data.message}</span>
                        </div>
                    `;
                    resetAnalysisUI();
                    showMessage('✅ Analysis completed successfully!', 'success');
                    break;
                    
                case 'error':
                    console.log('❌ Analysis error:', data.message);
                    statusContent.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="color: #ef4444; font-size: 20px;">❌</div>
                            <span style="color: #ef4444; font-weight: 600;">${data.message}</span>
                        </div>
                    `;
                    resetAnalysisUI();
                    showMessage(`❌ Analysis failed: ${data.message}`, 'error');
                    break;
                    
                case 'heartbeat':
                    console.log('💓 Heartbeat received');
                    // Just keep connection alive, no action needed
                    break;
                    
                default:
                    console.log('❓ Unknown message type:', data.type);
            }
        } catch (e) {
            console.error('❌ Error parsing progress data:', e, 'Raw data:', event.data);
        }
    };
    
    progressEventSource.onerror = function(event) {
        console.error('❌ Progress stream error:', event);
        console.log('EventSource readyState:', progressEventSource.readyState);
        
        // Only show error if analysis is still supposed to be running
        if (currentAnalysisSession) {
            showMessage('⚠️ Lost connection to analysis progress stream', 'warning');
        }
    };
}

// Stop analysis function
async function stopAnalysis() {
    if (!currentAnalysisSession) {
        showMessage('No analysis is currently running', 'warning');
        return;
    }
    
    try {
        const stopButton = document.getElementById('stop-analysis-btn');
        stopButton.disabled = true;
        stopButton.textContent = '🛑 Stopping...';
        
        const response = await fetch(`http://localhost:5000/api/analysis/stop/${currentAnalysisSession}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('🛑 Analysis stopped successfully', 'success');
            
            // Update status
            const statusContent = document.getElementById('status-content');
            statusContent.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="color: #f59e0b; font-size: 20px;">🛑</div>
                    <span style="color: #f59e0b; font-weight: 600;">Analysis stopped by user</span>
                </div>
            `;
        } else {
            throw new Error(result.error || 'Failed to stop analysis');
        }
        
    } catch (error) {
        console.error('Error stopping analysis:', error);
        showMessage(`❌ Failed to stop analysis: ${error.message}`, 'error');
    } finally {
        resetAnalysisUI();
    }
}

// Reset analysis UI to initial state
function resetAnalysisUI() {
    const runButton = document.getElementById('run-analysis-btn');
    const stopButton = document.getElementById('stop-analysis-btn');
    
    runButton.style.display = 'inline-flex';
    stopButton.style.display = 'none';
    stopButton.disabled = false;
    stopButton.textContent = '🛑 Stop Analysis';
    
    // Close progress stream
    if (progressEventSource) {
        progressEventSource.close();
        progressEventSource = null;
    }
    
    // Clear session
    currentAnalysisSession = null;
}

// View results function
function viewResults() {
    const selectedScenario = document.getElementById('analysis-scenario').value;
    
    if (!selectedScenario) {
        showMessage('Please select a scenario first', 'error');
        return;
    }
    
    showMessage(`📊 Opening results for ${selectedScenario.toUpperCase()} scenario`, 'success');
    
    // TODO: Implement results viewing - could open a new tab or modal with results
    console.log('View results for:', selectedScenario);
}

// Edit configuration function
function editConfiguration() {
    const selectedScenario = document.getElementById('analysis-scenario').value;
    
    if (!selectedScenario) {
        showMessage('Please select a scenario first', 'error');
        return;
    }
    
    // Switch to configuration tab
    switchTab('configuration');
    
    // Select the scenario in configuration tab
    const configScenarioSelect = document.getElementById('scenario');
    configScenarioSelect.value = selectedScenario;
    
    // Load the scenario
    loadScenario();
    
    showMessage(`✏️ Switched to configuration for ${selectedScenario.toUpperCase()} scenario`, 'success');
}

// Add download button functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add download button to output section
    const outputSection = document.getElementById('output');
    const existingButton = outputSection.querySelector('button');
    
    const downloadButton = document.createElement('button');
    downloadButton.textContent = '💾 Download JSON';
    downloadButton.onclick = downloadJSON;
    downloadButton.style.marginLeft = '10px';
    
    existingButton.insertAdjacentElement('afterend', downloadButton);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+S or Cmd+S to save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveConfiguration();
    }
    
    // Ctrl+E or Cmd+E to export
    if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportConfiguration();
    }
});

// Auto-save functionality
let autoSaveTimer;
document.addEventListener('input', function(e) {
    if (e.target.matches('#input-form input, #input-form textarea')) {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(() => {
            const scenarioSelect = document.getElementById('scenario');
            if (scenarioSelect.value) {
                saveConfiguration();
            }
        }, 2000); // Auto-save after 2 seconds of no input
    }
});
