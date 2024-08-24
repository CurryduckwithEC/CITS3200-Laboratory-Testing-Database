var URL = "http://127.0.0.1:5000";


/**
 * Form select functions for distance and category for sorting
 */
document.getElementById("distance").addEventListener("change", function(){
    var selected = this.value;
    //console.log(selected);
    filter_distance(selected);
});



/**
 * Takes location that matches route in API and assigns the
 * retrieved json to activities_json.
 */
async function get_activities(location){
    const response = await fetch(URL+ "/" + location);
    var activities_json = await response.json();
    return activities_json;
}


/**
 * render_cards uses the activities json to generate the cards
 * that are shown in the activities menu.
 * 
 * render_modal uses the activities json to generate the modal.
 * 
 * Both uses the id during the loop as the id for the html element to link
 * the modal to the card.
 */
function assign_id(activities_json){
    for (var i = 0; i < activities_json.length; ++i){
        activities_json[i]["id"] = i;
        //console.log(activities_json[i])
        //also convert unix timestamp to readable date
        activities_json[i]["Last_Updated"] = new Date(activities_json[i]["Last_Updated"]);
    }
}

function render_cards(activities_json){
    const template = $("#card-handlebars").html();
    const template_script = Handlebars.compile(template);

    for(var i = 0; i < activities_json.length; ++i){
        var context = activities_json[i];
        //console.log(context);
        var html = template_script(context);
        $("#main").append(html);
    }
}

function render_modal(activities_json){
    const template = $("#modal-handlebars").html();
    const template_script = Handlebars.compile(template);

    for(var i = 0; i < activities_json.length; ++i){
        var context = activities_json[i];
        //console.log(context);
        var html = template_script(context);
        $("#main").append(html);
    }
}

/**
 * Catch all to render both cards and modal.
 */

async function render_all(location){
    const activities_json = await get_activities(location)
    
    assign_id(activities_json);
    render_cards(activities_json);
    render_modal(activities_json);
    filter_distance(-1);
}


/**
 * filter_distance assigns the .show class to displayable elements within
 * the filter for distance
 * 
 * takes the distance that is being filtered by
 */
function filter_distance(distance){
    var buttons = document.getElementsByClassName("list-button");
    //console.log("loaded all")
    // -1 is All filter
    if(distance == -1){
        for(var i = 0; i < buttons.length; ++i){
            hide_element(buttons[i]);
            show_element(buttons[i]);
        }
    }
    else{
        for(var i = 0; i < buttons.length; ++i){
            var element_distance = buttons[i].querySelector("#sub_distance").innerText;
            element_distance = element_distance.replace("km", "");
            //console.log(element_distance);
            hide_element(buttons[i]);
            //console.log(Number(distance)==Number(element_distance));
            if(Number(distance) == Number(element_distance)){
                show_element(buttons[i]);
            }
        }
    }
}

function show_element(element){
    element.classList.add("show");
    //console.log(element);
}

function hide_element(element){
    if(element.classList.contains("show")){
        element.classList.remove("show");
    }
}