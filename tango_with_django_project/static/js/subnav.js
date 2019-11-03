/* toggles the left bar with categories & search
is used for small devices only */
function toggleBar(){
	let sidebar = document.getElementById("mySidebar");
	let mainElement = document.getElementById('main_content');
	
	if (sidebar.classList.contains('d-none')) {
		sidebar.classList.remove('d-none');	
	}
	else 
		sidebar.classList.add('d-none');
}