import { Injectable } from "@angular/core";
import { GeneralDataService } from "app/general-data.service";
import { RegionCountResponse, Region, SearchResponse, SortParameters, FilterParameters, SearchParameters, SortParameter } from 'app/interfaces/admin_interfaces';

@Injectable()
export class AdminDataService {
  generalDataService: GeneralDataService;
  constructor(private dataService: GeneralDataService) {
    this.generalDataService = dataService;
  }

  monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
  ];

  buildSortString(sortParameters: SortParameters): string {
    if (sortParameters.length == 0) 
      return "";

    let serverSortParameters = [...sortParameters];
    //Expand name into last_name, middle_name, first_name
    var indexOfName = serverSortParameters.findIndex(sp => sp.prop == "name");
    if (indexOfName >= 0) {
      var dir = serverSortParameters.find(sp => sp.prop == "name").dir;
      var nameArray : SortParameters = [
        { prop: "last_name",dir: dir }, 
        { prop: "first_name", dir: dir },
        { prop: "middle_name", dir: dir }
      ];
      serverSortParameters.splice(indexOfName,1,...nameArray);
    }

    //Handle ordering
    var orderingString = "&ordering=";
    serverSortParameters.forEach((order) => {
      var orderName = order.prop;
      if (order.dir === "desc") orderingString += "-";
      orderingString += `${orderName},`;
      //Remove trailing comma.
      if(serverSortParameters[serverSortParameters.length-1] === order){
        orderingString = orderingString.slice(0, -1);
       }
    });

    return orderingString;
  }

  buildFilterString(filterParameters: FilterParameters): string {
    return Object.keys(filterParameters)
      .filter((x) => filterParameters[x] !== null && filterParameters[x].toString().trim().length !== 0)
      .map((key) => {
        var snakeCaseKey = key.replace(
          /[A-Z]/g,
          (letter) => `_${letter.toLowerCase()}`
        );
        
        return `${encodeURIComponent(snakeCaseKey)}=${encodeURIComponent(
          filterParameters[key].toString().trim()
        )}`;
      })
      .join("&");
  }

  buildQueryString(searchParameters: SearchParameters): string {
    var filterString = this.buildFilterString(
      searchParameters.filterParameters
    );
    var sortString = this.buildSortString(searchParameters.sortParameters);
    return `?${filterString}${sortString}`;
  }

  buildDateString(targetDate: Date) : string {
    return new Date(targetDate).getDate() + "-" + this.monthNames[new Date(targetDate).getMonth()] + "-" + new Date(targetDate).getFullYear()
  }

  async getData(searchParameters: SearchParameters) {
    var action = this.buildQueryString(searchParameters);
    const url = this.generalDataService.getApiUrl("responses/" + action);
    console.log(url);
    return await this.generalDataService.loadJson(url) as SearchResponse;
  }

  async getSearchResponse(searchParameters: SearchParameters) : Promise<SearchResponse> {
    var searchResponse = await this.getData(searchParameters);

    searchResponse.results = searchResponse.results.map((r) => ({
      ...r,
      deadline_date: this.buildDateString(r.deadline_date as Date),
      created_date: this.buildDateString(r.created_date as Date),
      name: `${r.last_name}, ${r.first_name} ${r.middle_name || ''}`,
      hearing_location__name: r.hearing_location.name,
      originally_printed_by: r.printed_by !== null ? `${r.printed_by.first_name} ${r.printed_by.last_name} on ${this.buildDateString(r.printed_date)}` : ''
    }));

    return searchResponse;    
  }

  async getRegions() : Promise<Array<Region>>
  {
    const url = this.generalDataService.getApiUrl("regions/");
    console.log(url);
    return await this.generalDataService.loadJson(url) as Array<Region>;
  }

  async getCounts() : Promise<RegionCountResponse>
  {
    const url = this.generalDataService.getApiUrl("responses/counts/");
    console.log(url);
    return await this.generalDataService.loadJson(url) as RegionCountResponse;
  }

  public postGeneratePdf(targetPdfs) {

  }
}