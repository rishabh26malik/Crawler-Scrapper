const gui_ieee_map = {
    "AllField" : "Full Text .AND. Metadata",
    "Title":"Document Title",
    "ContribAuthor" : "Authors",
    "Abstract" : "Abstract",
    "Fulltext" : "Full Text Only",
    "Affiliation" : "Author Affiliations",
    "Keyword" : "Author Keywords",
    "ConferenceLocation" : "",
    "ConferenceSponsor" : "Funding Agency",
    "Contrib" : "Publication Title",
    "DOI" : "DOI",
    "PubIdSortField" : "ISBN"
};

const springer_map = {
    "Title" : "title-is",
    "ContribAuthor" : "author-is",
    "Abstract" : "all-words",
    "Fulltext" : "all-words",
    "AllField" : "all-words"
};

export function get_ieee_query_string(selection_list) {
    let first = selection_list[0];
    if(first === undefined || first === null) return "";
    
    let ieee_str = "";
    selection_list.shift();
    ieee_str += ("(\""+gui_ieee_map[first[0]]+"\":"+first[1]+")");
    
    for(let x of selection_list) {
        let str = "("+ieee_str;
        str += " "+x[0]+" ";
        str += "\""+gui_ieee_map[x[1]]+"\":"+x[2]+")";
        ieee_str = str;
    }
    
    return ieee_str;
}

export function get_acm_query_string(selection_list) {
    let first = selection_list[0];
    if(first === undefined || first === null) return "";
    
    let acm_str = ""; 
    acm_str += first[0]+":("+first[1]+")";
    selection_list.shift();

    for(let x of selection_list) {
        acm_str += " "+x[0]+" "+x[1]+":("+x[2]+")";
    }

    return acm_str;
}

export function get_springer_query_str(selection_list) {
    let first = selection_list[0];
    if(first === undefined || first === null) return "";
    
    let springer_query = {};
    if(first[0] in springer_map) 
        springer_query[springer_map[first[0]]] = first[1];
    
    selection_list.shift();
    for(let x of selection_list) {
        if(x[1] in first || springer_map[x[1]] in springer_query) {
            springer_query[springer_map[x[1]]] += " "+x[0]+" "+x[2];
        }else springer_query[springer_map[x[1]]] = x[2];
    } 
    
    delete springer_query["undefined"];
    delete springer_query["null"];
    return springer_query;
}

export function get_springer_query(query_s, filter) {
    if(filter === undefined || filter === null || filter === {}) return query_s;
    if(filter.from === "" && filter.to === "") return query_s;
    
    query_s["date-facet-mode"] = "between";
    query_s["facet-start-year"] = `${filter.from.split('-')[0]}`;
    query_s["facet-end-year"] = `${filter.to.split('-')[0]}`;
    
    return query_s;
}

export function get_ieee_query(query_str, filter) {
    let ranges_str = "";
    ranges_str = `${filter.from.split('-')[0]}_${filter.to.split('-')[0]}_Year`;
    
    if(ranges_str === "__Year") return {
        "queryText" : `${query_str}`
    };
    
    return {
        "queryText" : `${query_str}`,
        "ranges" : [`${ranges_str}`]
    };
}

export function get_acm_query(query_str, filter) {
    let pub_date="Publication Date: ("+ filter.from+" TO "+filter.to+")";
    if(filter.from === undefined || filter.from.length === 0) 
        return {
            "query" : `${query_str}`
        }
    
    return {
        "query" : `${query_str}`,
        "filter" : `${pub_date}`
    };
}

export function get_sd_query_string(selection_list) {
    if(selection_list === undefined || selection_list === null || selection_list.length === 0) 
        return {};
    
    let SD_query = {};
    let first = selection_list[0];
    
    switch(first[0]) {
        case "AllField": SD_query["qs"]=first[1];
                            break;
        case "Title" : SD_query["title"]=first[1];
                            break;
        case "ContribAuthor" : SD_query["authors"] = first[1];
                            break;
        case "PubIdSortField" : SD_query["docId"] = first[1];
                            break;
        case "Affiliation" : SD_query["affiliations"] = first[1];
                            break;
        case "Abstract" || "Keyword":
                            SD_query["tak"]=first[1];
                            break;
    }

    selection_list.shift();
    if(selection_list.length === 0) return SD_query;
    
    for (let x of selection_list){
        switch(x[1]){
            case "AllField":
                if(SD_query["qs"]==undefined){
                    SD_query["qs"]=x[2];
                }
                else{
                    SD_query["qs"]+=" "+x[0]+" "+x[2];
                }
                break;
            case "Title":
                if(SD_query["title"]==undefined){
                    SD_query["title"]=x[2];
                }
                else{
                    SD_query["title"]+=" "+x[0]+" "+x[2];
                }
                break;
            case "ContribAuthor":
                if(SD_query["authors"]==undefined){
                    SD_query["authors"]=x[2];
                }
                else{
                    SD_query["authors"]+=" "+x[0]+" "+x[2];
                }
                break;
            case "PubIdSortField":
                if(SD_query["docId"]==undefined){
                    SD_query["docId"]=x[2];
                }
                else{
                    SD_query["docId"]+=" "+x[0]+" "+x[2];
                }
                break;
            case "Affiliation":
                if(SD_query["affiliations"]==undefined){
                    SD_query["affiliations"]=x[2];
                }
                else{
                    SD_query["affiliations"]+=" "+x[0]+" "+x[2];
                }
                break;
            case "Abstract" || "Keyword":
                if(SD_query["tak"]==undefined){
                    SD_query["tak"]=x[2];
                }
                else{
                    SD_query["tak"]+=" "+x[0]+" "+x[2];
                }
                break;

        }
    }
    return SD_query;
}


export function get_sd_query(query, filter) {
    let date1 = filter.from;
    let date2 = filter.to;
    
    if(date1!="" && date2!=""){
        var fromyear=date1.split("-")[0];
        var toyear=date2.split("-")[0];
        if(date1!=date2){
            query["date"]=fromyear+"-"+toyear;
        }
    }
    
    return query;
}
