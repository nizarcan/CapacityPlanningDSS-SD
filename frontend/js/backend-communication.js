///////////////////////////////
// ARCHIVE LOADING FUNCTIONS //
///////////////////////////////
function getArchivePath() {
    eel.get_archive_path()(updateArchivePath)
}

function updateArchivePath(path){
    if (path != 0){
        console.log(path)
        document.getElementById("archivePathLabel").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("archivePathLabel")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}


function loadArchive(){
    if (document.getElementById("archivePathLabel").textContent == "Dosya Seçilmedi...") {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
    }
    else {
        eel.load_archive()
        document.location.href = "index.html"
    }

}

function goToRegister(){
    document.location.href = "register.html"
}


////////////////////////////////
// ANALYSIS LOADING FUNCTIONS //
////////////////////////////////
function getResultPath(fileType) {
    eel.get_result_path(fileType)(updateResultPath)
    }

function updateResultPath(path){
    if (Boolean(path)){
        console.log(path)
        document.getElementById("resultPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("resultPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

function getAnalysisDir() {
    eel.get_result_analysis_dir()(updateAnalysisDir)
    }

function updateAnalysisDir(path){
    if (Boolean(path)){
        console.log(path)
        document.getElementById("analysisDir").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("analysisDir")
        archivePathLabel.textContent = "Klasör Seçilmedi..."
    }
}

async function makeAnalysis(modelType){
    if (document.getElementById("resultPath").textContent == "Dosya Seçilmedi..." || document.getElementById("analysisDir").textContent == "Klasör Seçilmedi..."){
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
    }
    else {
        if (modelType == "tkpm") {
            let operationStatus = await eel.analyze_result('tkpm')()
        }
        else if (modelType == "okpm") {
            let operationStatus = await eel.analyze_result('okpm')()
        }
        else if (modelType == "okpb") {
            let operationStatus = await eel.analyze_result('okpb')()
        }
    }
    // There will be some function to raise indicating that the operation did not end correctly.
}

////////////////////////////////
//  INPUT CREATING FUNCTIONS  //
////////////////////////////////
function getPlan() {
    eel.get_plan()(updatePlan)
}

function updatePlan(path){
    if (path != 0){
        console.log(path)
        document.getElementById("planPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var planPathLabel = document.getElementById("planPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

function getSecondPlan() {
    eel.get_second_plan()(updateSecondPlan)
}

function updateSecondPlan(path){
    if (path != 0){
        console.log(path)
        document.getElementById("secondPlanPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var planPathLabel = document.getElementById("secondPlanPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

function getWorkdays() {
    eel.get_workdays()(updateWorkdays)
}

function updateWorkdays(path){
    if (path != 0){
        console.log(path)
        document.getElementById("workdaysPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var planPathLabel = document.getElementById("workdaysPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

function getSecondWorkdays() {
    eel.get_second_plan()(updateSecondWorkdays)
}

function updateSecondWorkdays(path){
    if (path != 0){
        console.log(path)
        document.getElementById("secondWorkdaysPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var planPathLabel = document.getElementById("secondWorkdaysPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

function getUpperModelOutput() {
    eel.get_upper_model_output()(updateUpperModelOutput)
}

function updateUpperModelOutput(path){
    if (path != 0){
        console.log(path)
        document.getElementById("upperModelOutputPath").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var planPathLabel = document.getElementById("upperModelOutputPath")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

eel.expose(raiseCreationErrorJs);
function raiseCreationErrorJs(){
    alert("1")
}

function createInputFile(inputType){
    if (inputType == "tkpm"){
        earlinessTardinessIds = ["erkenUretimComboBox", "gecUretimComboBox"]
        deviationProbabilityIds = ["birSigmaAltComboBox", "yarimSigmaAltComboBox", "sifirSigmaComboBox", "yarimSigmaUstComboBox", "birSigmaUstComboBox"]
        var earlinessTardinessPass = false
        var deviationProbabilitySum = 0
        var idOutputDirSelected = document.getElementById("inputFileOutputDir").value != "Klasör Seçilmedi..."
        for (let i=0; i<2; i++){
            earlinessTardinessPass = earlinessTardinessPass || Number(document.getElementById(earlinessTardinessIds[i]).value) != 0
        }

        for (let i=0; i<5; i++){
            deviationProbabilitySum = deviationProbabilitySum +  Number(document.getElementById(deviationProbabilityIds[i]).value)
        }
        if ((earlinessTardinessPass != true) || (deviationProbabilitySum != 1) || (!idOutputDirSelected)) {
            alert("SOMETHING is not right")
        }
        else {
            var earlinessTardiness = []
            var deviationProbabilities = []

            for (i=0; i<2; i++) {
                earlinessTardiness.push(Number(document.getElementById(earlinessTardinessIds[i]).value))
            }

            for (i=0; i<5; i++) {
                deviationProbabilities.push(Number(document.getElementById(deviationProbabilityIds[i]).value))
            }

            eel.create_input_file(inputType, earlinessTardiness, deviationProbabilities)
        }

    }
    else if (inputType == "okpm"){
        var labels = ["plan", "workdays", "upperModelOutput"]
        var passStatus = true
        for (i=0; i<3; i++) {
            passStatus = passStatus && document.getElementById(labels[i]+"Path").textContent != "Dosya Seçilmedi..."
        }
        passStatus = passStatus && document.getElementById("inputFileOutputDir").textContent != "Klasör Seçilmedi..."
        if (!passStatus) {
            alert("SOMETHING is not right")
        }
        else {
            eel.create_input_file(inputType, Number(document.getElementById("scenarioComboBox").value))
        }

    }
    else if (inputType == "okpb"){
        if (!document.getElementById("isDuplicateCheckBox").checked) {
            var labels = ["plan", "secondPlan", "workdays", "secondWorkdays", "upperModelOutput"]
            var passStatus = true
            for (i=0; i<5; i++) {
                passStatus = passStatus && document.getElementById(labels[i]+"Path").textContent != "Dosya Seçilmedi..."
            }
            passStatus = passStatus && document.getElementById("inputFileOutputDir").textContent != "Klasör Seçilmedi..."
            if (!passStatus) {
                alert("SOMETHING is not right")
            }
            else {
                eel.create_input_file(inputType, document.getElementById("isDuplicateCheckBox").checked)
            }
        }
        else {
            var labels = ["plan", "workdays", "upperModelOutput"]
            var passStatus = true
            for (i=0; i<3; i++) {
                passStatus = passStatus && document.getElementById(labels[i]+"Path").textContent != "Dosya Seçilmedi..."
            }
            passStatus = passStatus && document.getElementById("inputFileOutputDir").textContent != "Klasör Seçilmedi..."
            if (!passStatus) {
                alert("SOMETHING is not right")
            }
            else {
                eel.create_input_file(inputType, Number(document.getElementById("isDuplicateCheckBox").checked))
            }
        }
    }
}

function getOutputDir() {
    eel.get_input_file_output_dir()(updateOutputDir)
    }


function updateOutputDir(path){
    if (Boolean(path)){
        console.log(path)
        document.getElementById("inputFileOutputDir").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("inputFileOutputDir")
        archivePathLabel.textContent = "Klasör Seçilmedi..."
    }
}


////////////////////////////////
//  ARCHIVE UPDATE FUNCTIONS  //
////////////////////////////////
function showFileSelectionContainer(){
    var fileTypeIds = ["bom", "times", "order", "machineInfo", "tbd"]
    var selectedFileTypes = []
    for (i=0; i<5; i++) {
        if (document.getElementById(fileTypeIds[i]+"CheckBox").checked == true){
            selectedFileTypes.push(fileTypeIds[i])
        }
    }
    document.getElementById("fileSelectionContainer").style.display = "block"
    for (i=0; i<5; i++) {
        if (selectedFileTypes.includes(fileTypeIds[i])) {
            document.getElementById(fileTypeIds[i]+"Line").style.display = "block"
        }
        else {
            document.getElementById(fileTypeIds[i]+"Line").style.display = "none"
        }
    }
    document.getElementById("checkBoxContainer").style.display = "none"
}

function showCheckBoxContainer(){
    document.getElementById("checkBoxContainer").style.display = "block"
    document.getElementById("fileSelectionContainer").style.display = "none"
}

function updateArchive(){

    var fileTypeIds = ["bom", "times", "order", "machineInfo", "tbd"]
    var selectedFileTypes = []

    for (i=0; i<5; i++) {
        if (document.getElementById(fileTypeIds[i]+"CheckBox").checked == true){
            selectedFileTypes.push(fileTypeIds[i])
        }
    }

    for (i=0; i<selectedFileTypes.length; i++) {

    }
}



function launchFullScreen(element) {
  if(element.requestFullScreen) {
    element.requestFullScreen();
  } else if(element.mozRequestFullScreen) {
    element.mozRequestFullScreen();
  } else if(element.webkitRequestFullScreen) {
    element.webkitRequestFullScreen();
  }
}
