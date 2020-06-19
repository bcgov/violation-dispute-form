import { Injectable } from "@angular/core";
import { GeneralDataService } from "app/general-data.service";
import {
  SearchParameters,
  FilterParameters,
  SortParameters,
} from "./admin.component";


export interface SearchResponse {
  count: number;
  next: string;
  previous: string;
  results: Array<TicketResponseContent>;
}

interface TicketResponseContent {
  created_date: Date | string;
  updated_date: Date | string;
  emailed_date: Date | string;
 
  first_name: string;
  middle_name: string;
  last_name: string;

  email: string;

  hearing_attendance: string;
  hearing_location: string;

  ticket_number: string;
  ticket_date: Date;
  deadline_date: Date | string;
  dispute_type: string;
  pdf_filename: string;
  archived_by: string;
}

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

    var orderingString = "&ordering=";
    sortParameters.forEach((order) => {
      var orderName = order.prop;
      if (order.dir === "desc") orderingString += "-";
      if (orderName === "name") orderName = "last_name";
      orderingString += `${orderName},`;
    });

    //Remove trailing comma.
    if (sortParameters.length > 0) 
      orderingString = orderingString.slice(0, -1);
    return orderingString;
  }

  //Todo offset and limit.
  buildFilterString(filterParameters: FilterParameters): string {
    return Object.keys(filterParameters)
      .filter((x) => filterParameters[x].toString().trim().length !== 0)
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

  async getData(searchParameters: SearchParameters) {
    var action = this.buildQueryString(searchParameters);
    const url = this.generalDataService.getApiUrl("responses" + action);
    console.log(url);
    return await this.generalDataService.loadJson(url) as SearchResponse;
  }

  async getSearchResponse(searchParameters: SearchParameters) : Promise<SearchResponse> {
    var searchResponse = await this.getData(searchParameters);

    searchResponse.results = searchResponse.results.map((r) => ({
      ...r,
      deadline_date: new Date(r.deadline_date).getDate() + "-" + this.monthNames[new Date(r.deadline_date).getMonth()] + "-" + new Date(r.deadline_date).getFullYear(),
      created_date: new Date(r.created_date).getDate() + "-" + this.monthNames[new Date(r.created_date).getMonth()] + "-" + new Date(r.created_date).getFullYear(),
      name: `${r.last_name}, ${r.first_name} ${r.middle_name || ''}`,
    }));

    return searchResponse;    
  }

  //Not sure yet if we're passing file names or ids.
  public postGeneratePdf(targetPdfs) {
    //Get the selected
  }
}