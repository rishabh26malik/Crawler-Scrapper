import * as query_const from "./query_const.js";


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function updateParams(no_of_fields) {
    params = [];
    for(let i=1;i<=no_of_fields;i++){
        let id="#searchSelector"+String(i);
        let selected_id="#text"+String(i);
        let boolean_id="#booleanid"+String(i);
        if(i!=1) {
            params.push([$(boolean_id).val(), $(id).val(), $(selected_id).val()]);
        }
        else {
            params.push([$(id).val(), $(selected_id).val()]);
        }
            
    }
    return params;
}

function updateFilters() {
    let fromdate=$("#fromDate").val();
    let todate=$("#toDate").val();
    console.log(fromdate, typeof fromdate);
    return {
        from: fromdate, 
        to:todate
    };
}

let params = Array();

$(document).ready(function () {
    var requestData={};
    var fromdate,todate,value1;
    var no_of_fields = 1;
    const searchContainersMaster = document.querySelector(".MasterContainer");
    $("#addField").click(function () {
        if (no_of_fields < 10) {
            no_of_fields++;
            let newContainer = getDynamicSearchContainer(no_of_fields);
            searchContainersMaster.appendChild(newContainer);
        }
    });
    $("#removeField").click(function(){
        if (no_of_fields >1) {
            var id = "#searchContainer"+String(no_of_fields);
            $(id).remove();
            no_of_fields--;
        }
        
        
    });
    $(".MasterContainer").change(function(){

        let prms = JSON.parse(JSON.stringify(updateParams(no_of_fields)));
        let ieee_prms = JSON.parse(JSON.stringify(prms));
        let springer_prms = JSON.parse(JSON.stringify(prms));
        let sd_prms = JSON.parse(JSON.stringify(prms));

        let ieee_json = query_const.get_ieee_query(query_const.get_ieee_query_string(ieee_prms),updateFilters());
        let acm_json = query_const.get_acm_query(query_const.get_acm_query_string(prms), updateFilters());
        let springer_query =query_const.get_springer_query(query_const.get_springer_query_str(springer_prms), updateFilters());
        let sd_query = query_const.get_sd_query(query_const.get_sd_query_string(sd_prms), updateFilters());

        $("#searchQuery1").val(JSON.stringify(acm_json, null, 2));
        $("#ieeeQuery").val(JSON.stringify(ieee_json, null, 2));
        $("#springerQuery").val(JSON.stringify(springer_query, null, 2));
        $("#scienceDirectQuery").val(JSON.stringify(sd_query, null, 2));
    });

    var todaysDate = new Date(); 
    var year = todaysDate.getFullYear();        
    var month = ("0" + (todaysDate.getMonth() + 1)).slice(-2);  
    var day = ("0" + todaysDate.getDate()).slice(-2);           
    var maxDate = (year +"-"+ month +"-"+ day); 

    $('#fromDate').attr('max',maxDate);
    $('#toDate').attr('max',maxDate);

    $("#resetButton").click(function(){

        var value="";
        for(i=1;i<=no_of_fields;i++){
            id="#searchSelector"+String(i);
            selected_id="#text"+String(i);
            boolean_id="#booleanid"+String(i);
            if(i!=1)
                value+=" "+$(boolean_id).val()+" "+$(id).val()+":("+$(selected_id).val()+")";
            else
                value+=$(id).val()+":("+$(selected_id).val()+")";
        }
        $("#searchQuery").val(value);
        $("#searchQuery1").val('"query" :'+"{ "+value+" }");
    });
    $("#searchButton").click(function(){
        updateParams();

        requestData["ieeeQuery"] = query_const.get_ieee_query(
                query_const.get_ieee_query_string(updateParams(no_of_fields)), updateFilters());
        requestData["springerQuery"] = query_const.get_springer_query(
            query_const.get_springer_query_str(updateParams(no_of_fields)), updateFilters());
        requestData["sdQuery"] = query_const.get_sd_query(
            query_const.get_sd_query_string(updateParams(no_of_fields)), updateFilters());
        requestData["acmQuery"] = query_const.get_acm_query(
            query_const.get_acm_query_string(updateParams(no_of_fields)), updateFilters());

        console.log(requestData);

    $(".status").html("<b>Processing request. The zip file will start downloading automatically."+
            " Please wait for atleast 2-5 minutes. </b>")

    fetch("/search", {
        method: "POST",
        headers: {
            "Content-Type" : "application/json",
            "X-CSRFToken" : getCookie('csrftoken')
        },
        body: JSON.stringify(requestData)
    })
    .then((res) => {

        if(res.status !== 200) {
            $(".status").html(`<b>Error(code:${res.status}) occured while processing request. Please try again later</b>`);
            return ;
        }
        res.blob()
        .then((blob)=>{
            $(".status").html("<b>The file must be available for download.</b>")
            var url = window.URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = "citations_bibtex.zip";
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch((e)=>{
            $(".status").html(`Error occured while trying to download the zip file.`);
            console.error(`Error occured while making blob: ${e}`);
        });
    })
    .catch((e) => {
        $(".status").html(`Error occured while trying to sending request.`);
        console.error(`Error occured in request: ${e}`);
    });
    });

});

function getDynamicSearchContainer(no_of_fields) {
    let searchContainer = document.createElement("div");
    searchContainer.id = `searchContainer${no_of_fields}`;

    searchContainer.innerHTML = `
    <select id="booleanid${no_of_fields}" name="" style="height: 30px;width: 68px;">
        <option value="AND">AND</option>
        <option value="OR">OR</option>
        <option value="NOT">NOT</option>
        
    </select>
    <select id="searchSelector${no_of_fields}" class="searchContainer" style="height: 30px;width: 180px;" name="field${no_of_fields}">
        <option value="AllField" selected="selected">Anywhere</option>
        <option value="Title">Title</option>
        <option value="ContribAuthor">Author</option>
        <option value="Abstract">Abstract</option>
        <option value="Fulltext">Full text</option>
        <option value="Affiliation">Author Affiliation</option>
        <option value="Keyword">Author Keyword</option>
        <option value="ConferenceLocation">Conference Location</option>
        <option value="ConferenceSponsor">Conference Sponsor</option>
        <option value="Contrib">Name</option>
        <option value="PubIdSortField">ISBN/ISSN</option>
        <option value="DOI">DOI</option>
    </select>
    <label for="text${no_of_fields}" class="is-accessible">Search Term</label>
    <input id="text${no_of_fields}" type="text" placeholder="Enter Search term" value="" name="text${no_of_fields}">
    `;
    
    return searchContainer;
}
