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
    // console.log(gui_ieee_map["Keyword"]);
    selection_list.shift();
    ieee_str += ("(\""+gui_ieee_map[first[0]]+"\":"+first[1]+")");
    for(let x of selection_list) {
        // console.log(x[1], gui_ieee_map[x[1]]);
        let str = "("+ieee_str;
        str += " "+x[0]+" ";
        str += "\""+gui_ieee_map[x[1]]+"\":"+x[2]+")";
        ieee_str = str;
    }
    return ieee_str;
}

export function get_acm_query_string(selection_list) {
    // console.log(selection_list.length);
    let first = selection_list[0];
    if(first === undefined || first === null) return "";
    let acm_str = ""; 
    acm_str += first[0]+":("+first[1]+")";
    selection_list.shift();

    for(let x of selection_list) {
        acm_str += " "+x[0]+" "+x[1]+":("+x[2]+")";
    }
    // console.log(acm_str);
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
    // console.log(`get acm query: ${query_str}`);
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
