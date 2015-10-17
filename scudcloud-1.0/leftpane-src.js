var LeftPane = {
	addTeam: function(id, name, url, icon, active){
		var node = document.getElementById(id);
        if(node === null){
			var ul = document.getElementById('teams');
			li = document.createElement('li');
			li.id = id;
			li.setAttribute("onclick", "LeftPane.switchTo('"+id.replace(/'/g, '&quot;')+"','"+url.replace(/'/g, '&quot;')+"')");
			li.setAttribute("title", name);
			li.innerHTML = name[0];
			if( icon ){
			  li.style.backgroundImage = "url('"+ icon.replace(/'/g, '&quot;') +"')";
			  li.innerHTML = "";
			}
			ul.appendChild(li);
			if(active){
				LeftPane.setActive(id);
			}
			LeftPane.switchTo(id, url);
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
		leftPane.switchTo(url);
		LeftPane.setActive(id);
	},
	setActive: function(id){
		var list = document.getElementsByTagName("li");
		for(var i=0; i < list.length; i++){
			list[i].className = "inactive";
		}
		document.getElementById(id).className = "active";
	},
	clickNext: function(direction){
		var list = document.getElementsByTagName("li");
		
		var index = 0;
		for(; index < list.length; index++){
			if (list[index].className == "active") {
				break;			
			}
		}

		index += direction; //goto next one
		if (index >= list.length) {
			index = 0;
		} else if (index < 0) {
			index = list.length - 1;
		}
		
		LeftPane.click(index);
	}
};

