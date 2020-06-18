import { Component, OnInit } from "@angular/core";
import { ColumnMode, SelectionType, SortType } from "@swimlane/ngx-datatable";
import { NgbDateStruct } from "@ng-bootstrap/ng-bootstrap";
import { AdminDataService } from './admin-data.service';

//#region Interfaces
export interface SearchParameters {
  filterParameters: FilterParameters;
  sortParameters: SortParameters;
}

export interface FilterParameters {
  name: string;
  ticketNumber: string;
  createdDate: string;
  region: string;
  offset: number;
  limit: number;
}

export interface SortParameters extends Array<SortParameter> {}

interface SortParameter {
  prop: string;
  dir: string;
}

@Component({
  selector: "app-admin",
  templateUrl: "./admin.component.html",
  styleUrls: ["./admin.component.scss"],
})
export class AdminComponent implements OnInit {

  //#region Variables & Constructor
  AdminService: AdminDataService;

  ColumnMode = ColumnMode;
  SelectionType = SelectionType;
  SortType = SortType;
  reorderable = true;
  loading = false;
  columns = [
    { prop: "hearing_location", name: "Court Location" },
    { prop: "name", name: "Name" },
    { prop: "dispute_type", name: "Ticket Type" },
    { prop: "ticket_number", name: "Ticket #" },
    { prop: "created_date", name: "Response Date" },
    { prop: "deadline_date", name: "Deadline Date" },
    { prop: "action", name: "Action" }
  ];
  data = [];
  rows = [];
  selected = [];
  searchParameters: SearchParameters = {
    filterParameters: {
      name: "",
      ticketNumber: "",
      createdDate: "",
      region: "",
      offset: 0,
      limit: 0
    },
    sortParameters: [],
  };

  ngOnInit() {
    
  }

  constructor( private adminService: AdminDataService) {
    this.AdminService = adminService;

    //This will disable text highlighting while shift is held down.
    ["keyup", "keydown"].forEach((event) => {
      window.addEventListener(event, (e: KeyboardEvent) => {
        document.onselectstart = function () {
          return !(e.key == "Shift" && e.shiftKey);
        };
      });
    });

    this.searchParameters.sortParameters = [{ prop: 'hearing_location', dir: 'asc' }, { prop: 'name', dir: 'asc' }];
    this.executeSearch(this.searchParameters);
  }
  //#endregion Variables & Constructor

  async executeSearch(searchParameters: SearchParameters) {
    this.loading = true;
    this.data = await this.AdminService.getResponseSearch(this.searchParameters);
    this.loading = false;
    this.rows = this.data;
  }

  responseDateText() : string {
    if (this.searchParameters.filterParameters.createdDate == null)
     return 'All Response Dates';
    return `Response Date: ${this.searchParameters.filterParameters.createdDate}`
  }

  selectToday() {
    var date = new Date();
    var ngbDateStruct = { day: date.getDate(), month: date.getMonth() + 1, year: date.getFullYear()};
    this.searchParameters.filterParameters.createdDate = new Date().toISOString().slice(0,10);
    return ngbDateStruct;
  }

  filterByName(name: string) {
    this.searchParameters.filterParameters.name = name;
    this.executeSearch(this.searchParameters);
  }

  filterByRegion(region: string) {
    this.searchParameters.filterParameters.region = region;
    this.executeSearch(this.searchParameters);
  }

  filterByTicketNumber(ticketNumber: string) {
    this.searchParameters.filterParameters.ticketNumber = ticketNumber;
    this.executeSearch(this.searchParameters);
  }

  filterByResponseDate(responseNgbDate: NgbDateStruct) {
    this.searchParameters.filterParameters.createdDate = new Date(
      responseNgbDate.year,
      responseNgbDate.month - 1,
      responseNgbDate.day
    ).toISOString().slice(0,10);
    this.executeSearch(this.searchParameters);
  }

  sort(event) {
    console.log("Sort Event Triggered", event);
    this.loading = true;
    this.searchParameters.sortParameters = event.sorts;
    this.executeSearch(this.searchParameters);
  }

  select({ selected }) {  
    if (selected.length > 50) {
      this.selected = selected.slice(0,50);
      return;
    }
    this.selected.splice(0, this.selected.length);
    this.selected.push(...selected);
  }

  printSelected(event: MouseEvent) {
    //Get selected. 
    this.adminService.postGeneratePdf("5");
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
    this.adminService.postGeneratePdf(this.rows.slice(0,50));
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
  //#endregion Testing Data
}
