// ARCHIVE LOADING FUNCTIONS
function load_archive_file() {
    var data = document.getElementById("archive-path-getter").files[0]
    var reader = new FileReader()

    if (data){
        reader.readAsDataURL(data)
    }

    reader.onload = function(){
        eel.load_archive(reader.result)
    }
}

function setPathLabel(path){
	document.getElementById("archive_path_label").textContent = path
}

//ANALYZE FUNCTIONS
function get_result_path(){
	eel.get_excel_path()
}


function analyze_tkpm(){
	var file = document.getElementById("tkpmCiktisiInput").files[0]
	var reader = new FileReader()

	if (file){
		reader.readAsDataURL(file)
	}

	reader.onload = function(){
		eel.load_excel(reader.result)
	}
}


function resetAnalyzeSelection(){
    var fileSelect = document.getElementById("tkpmCiktisiInput")
    fileSelect.value = []
}

//hello
function get_input_file() {
    const file = document.querySelector('input[type=file]').files[0];
    const reader = new FileReader();
    if (file) {
        reader.readAsDataURL(file);
    }
	eel.get_input(document.querySelector('input[type=file]').files)
}

// Archive File Upload
function grab_archive(){
	var file = document.getElementById("file-upload").files[0]
	var reader = new FileReader()

	if (file){
		reader.readAsDataURL(file)
	}

	reader.onload = function(){
		eel.load_archive(reader.result)
	}

	//document.location.href = "index.html";
}
