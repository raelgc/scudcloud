var LeftPane = {
	addTeam: function(id, name, url){
		var node = document.getElementById(id);
        if(node == null){
			var ul = document.getElementById('teams');
			li = document.createElement('li');
			li.id = id;
			li.setAttribute("onclick", "leftPane.switchTo('"+url+"')")
			li.setAttribute("title", name)
			li.innerHTML = name[0];
			ul.appendChild(li);
		}
	}
}

