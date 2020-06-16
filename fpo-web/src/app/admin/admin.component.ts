import { Component, OnInit } from "@angular/core";
import { ColumnMode, SelectionType, SortType } from "@swimlane/ngx-datatable";
import { GeneralDataService } from "../general-data.service";
import { NgbDateStruct } from "@ng-bootstrap/ng-bootstrap";

//#region Interfaces
interface SearchParameters {
  filterParameters: FilterParameters;
  sortParameters: SortParameters;
}

interface SortParameters extends Array<SortParameter> {}
interface TicketResponse extends Array<TicketResponseContent> {}

interface SortParameter {
  prop: string;
  dir: string;
}

interface FilterParameters {
  name: string;
  ticketNumber: string;
  responseDate: string;
  region: string;
  offset: number;
  limit: number;
}

//Straight from TicketResponse.py.
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
//#endregion

@Component({
  selector: "app-admin",
  templateUrl: "./admin.component.html",
  styleUrls: ["./admin.component.scss"],
})
export class AdminComponent implements OnInit {

  //#region Variables & Constructor
  ColumnMode = ColumnMode;
  SelectionType = SelectionType;
  SortType = SortType;

  reorderable = true;

  columns = [
    { prop: "hearing_location", name: "Court Location" },
    { prop: "name", name: "Name" },
    { prop: "dispute_type", name: "Ticket Type" },
    { prop: "ticket_number", name: "Ticket #" },
    { prop: "created_date", name: "Response Date" },
    { prop: "deadline_date", name: "Deadline Date" },
    { prop: "action", name: "Action" }
  ];
  rows = [];
  loading = false;
  selected = [];
  searchParameters: SearchParameters = {
    filterParameters: {
      name: "",
      ticketNumber: "",
      responseDate: "",
      region: "",
      offset: 0,
      limit: 0
    },
    sortParameters: [],
  };

  ngOnInit() {
    
  }

  constructor(private dataService: GeneralDataService) {
    //This will disable text highlighting while shift is held down.
    ["keyup", "keydown"].forEach((event) => {
      window.addEventListener(event, (e: KeyboardEvent) => {
        document.onselectstart = function () {
          return !(e.key == "Shift" && e.shiftKey);
        };
      });
    });

    this.searchParameters.sortParameters = [{ prop: 'hearing_location', dir: 'asc' }, { prop: 'name', dir: 'asc' }];
    this.getSearch(this.searchParameters);
  }
  //#endregion Variables & Constructor

  //TODO move to service. 
  async getSearch(searchParameters: SearchParameters) {
    this.loading = true;
    
    var resultJson =  (await this.getData(
      searchParameters
    ));

    this.loading = false;

    this.data = resultJson.results.map(r => ({...r, name: `${r.last_name}, ${r.first_name} ${r.middle_name}`}));
    this.rows = this.data;
  }

  //TODO move to service. 
  async getData(searchParameters: SearchParameters) {
    var action = this.buildQueryString(searchParameters);
    const url = this.dataService.getApiUrl("responses/"+action);
    console.log(url);
    const response = await fetch(url);
    const json = await response.json();

    return json;
  }

  //TODO move to service.
  //Not sure yet if we're passing file names or ids.
  public postGeneratePdf(targetPdfs) {
    //Get the selected 
  }

  buildQueryString(searchParameters: SearchParameters): string {
    var filterString = this.buildFilterString(
      searchParameters.filterParameters
    );
    var sortString = this.buildSortString(searchParameters.sortParameters);
    return `?${filterString}${sortString}`;
  }

  //Todo offset and limit.
  buildFilterString(filterParameters: FilterParameters): string {
    return Object.keys(filterParameters)
      .filter(x => filterParameters[x].toString().trim().length !== 0)
      .map(
        (key) =>
        {
          var snakeCaseKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
          return `${encodeURIComponent(snakeCaseKey)}=${encodeURIComponent(filterParameters[key].toString().trim())}`;
        }
      )
      .join("&");
  }

  buildSortString(sortParameters: SortParameters): string {
    if (sortParameters.length == 0) return "";

    var orderingString = "&ordering=";
    sortParameters.forEach((order) => {
      var orderName = order.prop;
      if (order.dir === "desc") orderingString += "-";
      if (orderName === "name") orderName = "last_name";
      orderingString += `${orderName},`;
    });

    //Remove trailing comma.
    if (sortParameters.length > 0) orderingString = orderingString.slice(0, -1);

    return orderingString;
  }

  selectToday() {
    var date = new Date();
    var ngbDateStruct = { day: date.getDate(), month: date.getMonth() + 1, year: date.getFullYear()};
    this.searchParameters.filterParameters.responseDate = new Date().toISOString().slice(0,10);
    return ngbDateStruct;
  }

  responseDateText() : string {
    if (this.searchParameters.filterParameters.responseDate == null)
     return 'All Response Dates';
    return `Response Date: ${this.searchParameters.filterParameters.responseDate}`
  }

  filterByName(name: string) {
    this.searchParameters.filterParameters.name = name;
    this.getSearch(this.searchParameters);
  }

  filterByRegion(region: string) {
    this.searchParameters.filterParameters.region = region;
    this.getSearch(this.searchParameters);
  }

  filterByTicketNumber(ticketNumber: string) {
    this.searchParameters.filterParameters.ticketNumber = ticketNumber;
    this.getSearch(this.searchParameters);
  }

  filterByResponseDate(responseNgbDate: NgbDateStruct) {
    this.searchParameters.filterParameters.responseDate = new Date(
      responseNgbDate.year,
      responseNgbDate.month - 1,
      responseNgbDate.day
    ).toISOString().slice(0,10);
    this.getSearch(this.searchParameters);
  }

  sort(event) {
    //debugger;
    console.log("Sort Event Triggered", event);
    this.loading = true;
    this.searchParameters.sortParameters = event.sorts;
    this.getSearch(this.searchParameters);
  }

  select({ selected }) {
    //TODO limit 50 selections here. 
    console.log("Event: select", event, this.selected);
    this.selected.splice(0, this.selected.length);
    this.selected.push(...selected);
  }

  printSelected(event: MouseEvent) {
    //Get selected. 
    //this.postGeneratePdf()
    console.log(this.selected);
    event.preventDefault(); 
    event.stopPropagation();
    var oWindow = window.open("assets/doc.pdf", "print");
    oWindow.print();
    oWindow.close();
  }


  printTop50(event) {
    console.log(this.rows.slice(0,50));
    event.stopPropagation();
    //Get top 50 rows. 
    //this.postGeneratePdf(targetPdf)
    var oWindow = window.open("assets/doc.pdf", "print");
    oWindow.print();
    oWindow.close();
  }

  
  openPdf(event: MouseEvent) {
    event.preventDefault(); 
    event.stopPropagation();
    window.open("assets/doc.pdf");
  }

  //#region Testing Data
  regions = [
    { name: "All Regions" },
    { name: "Vancouver (Robson Square)" },
    { name: "Richmond, Surrey, Abbotsford" },
    { name: "Chilliwack, New Westminster, Port Coquitlam, North Vancouver, Pemberton, Bella Bella, Bella Coola, Klemtu, Sechelt"},
    { name: "Rest of province" },
  ];

  data = [];
  //#endregion Testing Data
}
