Attribute VB_Name = "DistilleryModelVBA"
'**************************************************************************************************
' Module:       DistilleryModelVBA
' Author:       Factory Assistant
' Date:         July 8, 2025
' Description:  This module contains a comprehensive set of VBA macros for automating and
'               enhancing the Distillery Financial Model. It includes procedures for scenario
'               management, goal-seeking, sensitivity analysis, data refreshing, and PDF
'               reporting. This code is designed to be production-ready for enterprise use.
'**************************************************************************************************

Option Explicit

' --- INSTRUCTIONS FOR WORKSHEET_CHANGE EVENT ---
' To automatically trigger the scenario update when the dropdown on the "Control Panel" is changed,
' you must place the following code in the sheet's own code module.
' 1. Right-click the "Control Panel" sheet tab in Excel.
' 2. Select "View Code".
' 3. Paste the code below into the code window that appears.
'
' Private Sub Worksheet_Change(ByVal Target As Range)
'     On Error GoTo ErrorHandler
'
'     ' Check if the changed cell is the "SelectedScenario" named range
'     If Not Intersect(Target, Me.Range("SelectedScenario")) Is Nothing Then
'         Application.EnableEvents = False
'         Call UpdateScenario
'         Application.EnableEvents = True
'     End If
'
'     Exit Sub
'
' ErrorHandler:
'     MsgBox "An error occurred in the Worksheet_Change event: " & Err.Description, vbCritical
'     Application.EnableEvents = True
' End Sub
' ------------------------------------------------------------------------------------------------

' ==================================================================================================
' == MAIN SUBROUTINES (CALLED FROM RIBBON OR EVENTS)
' ==================================================================================================

' --- 1. Update Scenario based on Control Panel selection ---
Public Sub UpdateScenario()
    Dim oldScreenUpdating As Boolean
    Dim oldCalculation As XlCalculation
    Dim scenarioName As String

    On Error GoTo ErrorHandler

    ' Store current application settings and optimize for speed
    oldScreenUpdating = Application.ScreenUpdating
    oldCalculation = Application.Calculation
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    scenarioName = ThisWorkbook.Sheets("Control Panel").Range("SelectedScenario").Value
    Application.StatusBar = "Updating model to '" & scenarioName & "' scenario..."

    ' The model's formulas are driven by the "SelectedScenario" named range.
    ' We just need to force a full recalculation of the entire workbook.
    Application.CalculateFull

    ' Refresh dependent objects (placeholders for specific implementation)
    Call RefreshAllCharts
    Call UpdateConditionalFormatting

    Application.StatusBar = "Scenario '" & scenarioName & "' update complete."
    ' Schedule status bar to be cleared after 2 seconds
    Application.OnTime Now + TimeValue("00:00:02"), "ClearStatus"

CleanExit:
    ' Restore original application settings
    Application.ScreenUpdating = oldScreenUpdating
    Application.Calculation = oldCalculation
    Exit Sub

ErrorHandler:
    MsgBox "An error occurred while updating the scenario: " & vbCrLf & Err.Description, vbCritical, "Scenario Update Error"
    Application.StatusBar = False
    Resume CleanExit
End Sub

' --- 2. Goal Seek to find the required input for a target IRR ---
Public Sub GoalSeekTargetIRR()
    Dim targetIRR As Variant
    Dim originalPrice As Double
    Dim result As String
    Dim changingCell As Range
    
    On Error GoTo ErrorHandler

    ' Prompt user for target IRR
    targetIRR = Application.InputBox("Enter your target Project IRR (e.g., 0.25 for 25%):", "Goal Seek for Target IRR", Type:=1)
    
    ' Check if user cancelled
    If VarType(targetIRR) = vbBoolean And targetIRR = False Then Exit Sub
    If Not IsNumeric(targetIRR) Then Exit Sub

    Set changingCell = ThisWorkbook.Sheets("Assumptions").Range("Avg_Price_per_Bottle")
    
    ' Save original value
    originalPrice = changingCell.Value
    
    Application.StatusBar = "Running Goal Seek to achieve " & Format(targetIRR, "0.0%") & " IRR..."

    ' Perform Goal Seek
    If ThisWorkbook.Sheets("Returns Analysis").Range("Project_IRR").GoalSeek(Goal:=targetIRR, ChangingCell:=changingCell) Then
        result = "Goal Seek Successful!" & vbCrLf & vbCrLf & _
                 "To achieve an IRR of " & Format(targetIRR, "0.0%") & "," & vbCrLf & _
                 "the Average Price per Bottle must be: " & Format(changingCell.Value, "$#,##0.00") & vbCrLf & _
                 "(Original Price was: " & Format(originalPrice, "$#,##0.00") & ")"
        MsgBox result, vbInformation, "Goal Seek Complete"
    Else
        MsgBox "Goal Seek could not find a solution. The model may be structured in a way that a solution is not possible, or the target is out of range.", vbExclamation, "Goal Seek Failed"
        ' Restore original value if failed
        changingCell.Value = originalPrice
    End If

CleanExit:
    Application.StatusBar = False
    Exit Sub

ErrorHandler:
    MsgBox "An error occurred during Goal Seek: " & vbCrLf & Err.Description, vbCritical, "Goal Seek Error"
    If Not changingCell Is Nothing Then changingCell.Value = originalPrice
    Resume CleanExit
End Sub

' --- 3. Run a two-way sensitivity analysis for Price vs. Volume Growth ---
Public Sub RunSensitivity()
    Dim wsAssumptions As Worksheet, wsReturns As Worksheet
    Dim originalPrice As Double, originalGrowth As Double
    Dim oldScreenUpdating As Boolean, oldCalculation As XlCalculation
    Dim priceVars As Variant, growthVars As Variant
    Dim r As Long, c As Long, totalSteps As Long, currentStep As Long

    On Error GoTo ErrorHandler

    ' Initialize worksheets
    Set wsAssumptions = ThisWorkbook.Sheets("Assumptions")
    Set wsReturns = ThisWorkbook.Sheets("Returns Analysis")

    ' Store current application settings and optimize for speed
    oldScreenUpdating = Application.ScreenUpdating
    oldCalculation = Application.Calculation
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    ' Save original input values
    originalPrice = wsAssumptions.Range("Avg_Price_per_Bottle").Value
    originalGrowth = wsAssumptions.Range("Annual_Growth_Rate").Value

    ' Define sensitivity ranges from the "Returns Analysis" sheet headers
    priceVars = Application.Transpose(wsReturns.Range("A33:A37").Value)
    growthVars = wsReturns.Range("B32:F32").Value
    
    totalSteps = UBound(priceVars) * UBound(growthVars, 2)
    currentStep = 0

    ' Loop through sensitivity ranges and populate the data table
    For r = LBound(priceVars) To UBound(priceVars)
        For c = LBound(growthVars, 2) To UBound(growthVars, 2)
            currentStep = currentStep + 1
            Application.StatusBar = "Running Sensitivity Analysis: " & Format(currentStep / totalSteps, "0%") & " complete..."

            ' Update assumption values
            wsAssumptions.Range("Avg_Price_per_Bottle").Value = originalPrice * (1 + priceVars(r))
            wsAssumptions.Range("Annual_Growth_Rate").Value = originalGrowth + growthVars(1, c)
            
            ' Recalculate and capture result
            Application.CalculateFull
            wsReturns.Range("IRR_Sensitivity_Table").Cells(r, c).Value = wsReturns.Range("Project_IRR").Value
        Next c
    Next r

    MsgBox "Sensitivity analysis is complete.", vbInformation, "Analysis Complete"

CleanExit:
    ' Restore original inputs
    If Not wsAssumptions Is Nothing Then
        wsAssumptions.Range("Avg_Price_per_Bottle").Value = originalPrice
        wsAssumptions.Range("Annual_Growth_Rate").Value = originalGrowth
    End If
    
    ' Restore application settings
    Application.ScreenUpdating = oldScreenUpdating
    Application.Calculation = oldCalculation
    Application.StatusBar = False
    Exit Sub

ErrorHandler:
    MsgBox "An error occurred during the sensitivity analysis: " & vbCrLf & Err.Description, vbCritical, "Sensitivity Analysis Error"
    Resume CleanExit
End Sub

' --- 4. Refresh all Power Query connections for actuals data ---
Public Sub RefreshActuals()
    Dim oldScreenUpdating As Boolean
    On Error GoTo ErrorHandler

    oldScreenUpdating = Application.ScreenUpdating
    Application.ScreenUpdating = False
    
    Application.StatusBar = "Refreshing all data connections (Power Query)... Please wait."
    
    ' Trigger the refresh
    ThisWorkbook.RefreshAll
    
    ' After refresh, update the data source mode and recalculate variances
    ThisWorkbook.Sheets("Control Panel").Range("DataSourceMode").Value = "Actuals + Forecast"
    Application.CalculateFull
    
    Application.StatusBar = "Data connections refreshed and variances recalculated."
    Application.OnTime Now + TimeValue("00:00:02"), "ClearStatus"

CleanExit:
    Application.ScreenUpdating = oldScreenUpdating
    Exit Sub

ErrorHandler:
    MsgBox "An error occurred while refreshing data: " & vbCrLf & Err.Description, vbCritical, "Data Refresh Error"
    Resume CleanExit
End Sub

' --- 5. Export key sheets to a board-ready PDF presentation ---
Public Sub ExportToPDF()
    Dim sheetsToPrint As Variant
    Dim pdfFileName As String
    Dim scenarioName As String, timeStamp As String
    
    On Error GoTo ErrorHandler

    ' Define sheets for the presentation
    sheetsToPrint = Array("Cover", "Dashboard", "Income Statement", "Cash Flow Statement", "Balance Sheet")
    
    ' Generate dynamic filename
    scenarioName = ThisWorkbook.Sheets("Control Panel").Range("SelectedScenario").Value
    timeStamp = Format(Now, "YYYYMMDD_HHMMSS")
    pdfFileName = ThisWorkbook.Path & Application.PathSeparator & "Distillery Board Presentation_" & scenarioName & "_" & timeStamp & ".pdf"
    
    Application.StatusBar = "Generating Board Presentation PDF..."
    
    ' Select the sheets and export
    ThisWorkbook.Sheets(sheetsToPrint).Select
    
    ActiveSheet.ExportAsFixedFormat Type:=xlTypePDF, _
                                    Filename:=pdfFileName, _
                                    Quality:=xlQualityStandard, _
                                    IncludeDocProperties:=True, _
                                    IgnorePrintAreas:=False, _
                                    OpenAfterPublish:=True
                                    
    ' Return to the control panel
    ThisWorkbook.Sheets("Control Panel").Activate
    
    MsgBox "Board Presentation PDF has been created successfully and opened for review.", vbInformation, "PDF Export Complete"

CleanExit:
    Application.StatusBar = False
    Exit Sub

ErrorHandler:
    MsgBox "An error occurred during PDF export: " & vbCrLf & Err.Description, vbCritical, "PDF Export Error"
    Resume CleanExit
End Sub


' ==================================================================================================
' == HELPER FUNCTIONS
' ==================================================================================================

' --- Clears the application status bar ---
Public Sub ClearStatus()
    Application.StatusBar = False
End Sub

' --- Placeholder for refreshing all charts (requires specific chart names) ---
Public Sub RefreshAllCharts()
    ' This is a placeholder. A full implementation would loop through specific
    ' chart objects on the dashboard and other sheets to refresh their data source.
    ' Example:
    ' Dim chObj As ChartObject
    ' For Each chObj In ThisWorkbook.Sheets("Dashboard").ChartObjects
    '     chObj.Chart.Refresh
    ' Next chObj
End Sub

' --- Placeholder for updating conditional formatting ---
Public Sub UpdateConditionalFormatting()
    ' Conditional formatting is usually updated automatically upon recalculation.
    ' This sub is a placeholder in case manual intervention is ever needed.
End Sub


' ==================================================================================================
' == CUSTOM RIBBON XML
' ==================================================================================================
'
' This XML can be used with the "Custom UI Editor for Microsoft Office" to create a
' custom ribbon tab for this financial model.
'
' <customUI xmlns="http://schemas.microsoft.com/office/2009/07/customui">
'   <ribbon>
'     <tabs>
'       <tab id="distilleryModelTab" label="Distillery Model" insertAfterMso="TabHome">
'
'         <group id="grpScenarioTools" label="Scenario Tools">
'           <button id="btnUpdateScenario"
'                   label="Update Active Scenario"
'                   size="large"
'                   onAction="UpdateScenario"
'                   imageMso="Refresh"
'                   screentip="Update Model"
'                   supertip="Recalculates the entire model based on the 'SelectedScenario' dropdown on the Control Panel."/>
'         </group>
'
'         <group id="grpAnalysisTools" label="Analysis Tools">
'           <button id="btnGoalSeek"
'                   label="Goal Seek Target IRR"
'                   size="large"
'                   onAction="GoalSeekTargetIRR"
'                   imageMso="GoalSeek"
'                   screentip="IRR Goal Seek"
'                   supertip="Find the required 'Average Price per Bottle' to achieve a specific target IRR."/>
'           <button id="btnRunSensitivity"
'                   label="Run Sensitivity Analysis"
'                   size="large"
'                   onAction="RunSensitivity"
'                   imageMso="TableSelect"
'                   screentip="Run Sensitivity"
'                   supertip="Runs a two-way sensitivity analysis for Price vs. Volume Growth and populates the data table on the 'Returns Analysis' sheet."/>
'         </group>
'
'         <group id="grpDataManagement" label="Data Management">
'           <button id="btnRefreshActuals"
'                   label="Refresh Actuals Data"
'                   size="large"
'                   onAction="RefreshActuals"
'                   imageMso="DataRefreshAll"
'                   screentip="Refresh Data"
'                   supertip="Refreshes all Power Query connections to import the latest actuals data."/>
'         </group>
'
'         <group id="grpReporting" label="Reporting">
'           <button id="btnExportPDF"
'                   label="Export Board PDF"
'                   size="large"
'                   onAction="ExportToPDF"
'                   imageMso="FileSaveAsPdfOrXps"
'                   screentip="Export to PDF"
'                   supertip="Creates a board-ready PDF presentation including the Cover, Dashboard, and key financial statements."/>
'         </group>
'
'       </tab>
'     </tabs>
'   </ribbon>
' </customUI>
'
' ==================================================================================================
