import { Injectable } from "@angular/core";
import { GeneralDataService } from "app/general-data.service";
import { HttpClient } from "@angular/common/http";
import {
  SearchParameters,
  FilterParameters,
  SortParameters,
} from "./admin.component";

interface SearchResult {
  count: number;
  next: number;
  previous: number;
  results: Array<TicketResponseContent>;
}

interface TicketResponseContent {
  created_date: string;
  updated_date: string;
  emailed_date: string;
 
  first_name: string;
  middle_name: string;
  last_name: string;

  email: string;

  hearing_attendance: string;
  hearing_location: string;

  ticket_number: string;
  ticket_date: Date;
  deadline_date: Date;
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
    const url = this.generalDataService.getApiUrl("responses/" + action);
    console.log(url);
    return await this.generalDataService.loadJson(url) as SearchResult;
  }

  async getResponseSearch(searchParameters: SearchParameters) {
    var resultJson = await this.getData(searchParameters);
    return resultJson.results.map((r) => ({
      ...r,
      name: `${r.last_name}, ${r.first_name} ${r.middle_name || ''}`,
    }));
  }

  //Not sure yet if we're passing file names or ids.
  public postGeneratePdf(targetPdfs) {
    //Get the selected
  }
}