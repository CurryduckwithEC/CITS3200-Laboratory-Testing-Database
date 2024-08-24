var URL = "http://127.0.0.1:5000";

var current_distance_filter = -1; 
var current_category_filter = -1;

/**
 * Form select functions for distance and category for sorting
 */
document.getElementById("distance").addEventListener("change", function(){
    var selected = this.value;
    //console.log(selected);
    filter_distance(selected);
});

document.getElementById("category").addEventListener("change", function(){
    var selected = this.value;
    filter_category(selected);
})


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

//TODO: find a way to allow sorting by both category and distance

/**
 * filter_distance assigns the .show class to displayable elements within
 * the filter for distance
 * 
 * takes the distance that is being filtered by
 */
function filter_distance(distance){
    // set current filter category
    set_distance_filter(distance);
    console.log("Distance filter: ", distance);
    var buttons = document.getElementsByClassName("list-button");

    // -1 is All filter
    if(distance == -1){
        for(var i = 0; i < buttons.length; ++i){
            //console.log("loaded all")
            hide_element(buttons[i]);
            console.log(current_category_filter);
            if(get_category_value(buttons[i]).includes(current_category_filter) || current_category_filter == -1){
                show_element(buttons[i]);
            }
        }
    }
    else{
        for(var i = 0; i < buttons.length; ++i){
            var element_distance = get_distance_value(buttons[i]);
            var element_category = get_category_value(buttons[i]);
            //console.log(element_distance);
            hide_element(buttons[i]);
            //console.log(Number(distance)==Number(element_distance));
            if(
                Number(distance) == Number(element_distance) && 
                (element_category.includes(current_category_filter) || current_category_filter == -1)
                ){
                show_element(buttons[i]);
            }
        }
    }
}

/**
 * filter_category assigns the .show class to displayable elements within the filter
 * for category
 * 
 * functions mainly based off searching the substring of the category displayed in the
 * card
 */
function filter_category(category){
    //set the current filter category
    set_category_filter(category);

    console.log("Category filter: ", category);
    var buttons = document.getElementsByClassName("list-button");
    console.log(category);
    // -1 is All filter
    if(category == -1){
        for(var i = 0; i < buttons.length; ++i){
            hide_element(buttons[i]);
            if(get_distance_value(buttons[i]) == current_distance_filter || current_distance_filter == -1){
                show_element(buttons[i]);
            }
        }
    }
    else{
        for(var i = 0; i < buttons.length; ++i){
            var element_category = get_category_value(buttons[i]);
            var element_distance = get_distance_value(buttons[i]);
            hide_element(buttons[i]);
            console.log(element_category);
            if(
                element_category.includes(category) && 
                (element_distance == current_distance_filter || current_distance_filter == -1)
                ){
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

/**
 * get_distance_value and get_category_value retrieves the distance and category
 * value from the button DOM object respectively which allows for easier sorting
 * by multiple filters
 */
function get_distance_value(element){
    var distance = element.querySelector("#sub_distance").innerText;
    distance = distance.replace("km", "");
    distance = Number(distance);     // cast to int preventing type issues
    return distance;
}

function get_category_value(element){
    var category = element.querySelector("#sub_category").innerText.toLowerCase();
    return category;
}

/**
 * Setter functions for current filter status, filters start with all (-1)
 */
function set_distance_filter(new_value){
    current_distance_filter = Number(new_value);
}

function set_category_filter(new_value){
    current_category_filter = new_value;
}