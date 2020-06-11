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
    if (operationStatus) {
        alert("Analiz başarıyla sonuçlandı.")
    }
    else {
        alert("Analiz sırasında bir problem oluştu. Lütfen girdiğiniz verinin doğruluğunu kontrol ediniz.")
    }
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
    alert("Girdi dosyası oluşturulması sırasında beklenmedik bir problem oluştu. Dosyalarınızın doğruluğunu kontrol ediniz.")
}

eel.expose(raiseForecastStartedAlert);
function raiseForecastStartedAlert(){
    alert("Talep tahminlemesi başladı.")
}

eel.expose(raiseForecastEndedAlert);
function raiseForecastEndedAlert(){
    alert("Talep tahminlemesi işlemi sona erdi. Girdi dosyası oluşturuluyor.")
}

eel.expose(raiseInputCreationSuccessAlert);
function raiseInputCreationSuccessAlert(){
    alert("Dosya oluşturulması başarıyla tamamlandı.")
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
            alert("Lütfen girdilerin doğruluğunu kontrol edin.")
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

            var forecastCheckboxChecked = document.getElementById("forecastCheckBox").checked

            eel.create_input_file(inputType, earlinessTardiness, deviationProbabilities, forecastCheckboxChecked)
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
            alert("Lütfen girdilerin doğruluğunu kontrol edin.")
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
                alert("Lütfen girdilerin doğruluğunu kontrol edin.")
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
                alert("Lütfen girdilerin doğruluğunu kontrol edin.")
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
    eel.update_archive(selectedFileTypes)
}

function getNewFilePath(fileType){
    currentFileType = fileType
    eel.update_new_file_path(fileType)(updateNewFilePath)
}

function updateNewFilePath(path){
    if (path != 0){
        console.log(path)
        document.getElementById(currentFileType + "Path").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("archivePathLabel")
        archivePathLabel.textContent = "Dosya Seçilmedi..."
    }
}

////////////////////////////////
// SUMMARY CREATING FUNCTIONS //
////////////////////////////////
function getSummaryDir(){
    eel.get_summary_dir()(updateSummaryDir)
}

function updateSummaryDir(path){
    if (path != 0){
        console.log(path)
        document.getElementById("summaryDir").textContent = path
    }
    else {
        var alertBox = document.getElementById("noFileSelectedAlert")
        alertBox.style.display = "block"
        var archivePathLabel = document.getElementById("summaryDir")
        archivePathLabel.textContent = "Klasör Seçilmedi..."
    }
}

async function createSummary() {
    var fileTypeIds = ["bom", "times", "order", "machineInfo", "tbd"]
    var selectedFileTypes = []

    for (i=0; i<5; i++) {
        if (document.getElementById(fileTypeIds[i]+"CheckBox").checked == true){
            selectedFileTypes.push(fileTypeIds[i])
        }
    }
    console.log(selectedFileTypes)
    let completionStatus = await eel.create_summary(selectedFileTypes)()
    if (Boolean(completionStatus)) {
        alert("İşlem başarıyla sonuçlandı.")
    }
    else {
        alert("İşlem sırasında bir hata oluştu")
    }

}

////////////////////////////////
// ARCHIVE CREATING FUNCTIONS //
////////////////////////////////
async function createArchive(){
    var fileTypeIds = ["bom", "times", "order", "machineInfo", "tbd"]
    var isAllSelected=true
    for (i=0; i<5; i++) {
        isAllSelected = isAllSelected && (document.getElementById(fileTypeIds[i] + "Path") != "Dosya Seçilmedi...")
    }
    if (isAllSelected) {
        let creationStatus = await eel.create_archive()()
        if (Boolean(creationStatus)) {
            document.location.href = "index.html"
        }
        else {
            alert("Bir hata oluştu, lütfen dosyaların doğruluğundan emin olup tekrar deneyiniz.")
        }
    }
    else {
        alert("Eklenmemiş dosya(lar) bulunmaktadır. Lütfen tüm dosyaları seçin.")
    }
}

////////////////////////////////
//      LOGOUT FUNCTIONS      //
////////////////////////////////
async function logOutApp(){
    let logoutStatus = await eel.logout_app()()
    if (logoutStatus) {
        alert("İşlem tamamlandı, programı kapatabilirsiniz.")
    }
    else {
        alert("Bir hata oluştu, lütfen tekrar deneyiniz.")
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

eel.expose(createAlert);
function createAlert(alertMessage){
    alert(alertMessage)
}