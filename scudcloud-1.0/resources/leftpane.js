var LeftPane = {
	addTeam: function(id, name, url, active){
		var node = document.getElementById(id);
        if(node == null){
			var ul = document.getElementById('teams');
			li = document.createElement('li');
			li.id = id;
			li.setAttribute("onclick", "LeftPane.switchTo('"+id+"','"+url+"')")
			li.setAttribute("title", name)
			li.innerHTML = name[0];
			ul.appendChild(li);
			if(active) LeftPane.setActive(id);
		}
	},
	click: function(i){
		var list = document.getElementsByTagName("li");
		for(var j=0; j < list.length; j++){
			if(i==j){
				list[j].click();
				break;
			}
		}
	},
	alert: function(team){
		document.getElementById(team).classList.add('alert');
	},
	stopAlert: function(team){
		document.getElementById(team).classList.remove('alert');
	},
	switchTo: function(id, url){
		leftPane.switchTo(url)
		LeftPane.setActive(id);
	},
	setActive: function(id){
		var list = document.getElementsByTagName("li");
		for(var i=0; i < list.length; i++){
			list[i].className = "inactive";
		}
		document.getElementById(id).className = "active";
	}
}

