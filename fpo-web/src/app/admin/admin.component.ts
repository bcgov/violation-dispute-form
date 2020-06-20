import { Component, OnInit, ElementRef } from "@angular/core";
import { ColumnMode, SelectionType, SortType } from "@swimlane/ngx-datatable";
import { NgbDateStruct } from "@ng-bootstrap/ng-bootstrap";
import { AdminDataService, SearchResponse } from './admin-data.service';

//#region Interfaces
export interface SearchParameters {
  filterParameters: FilterParameters;
  sortParameters: SortParameters;
}

export interface FilterParameters {
  search: string;
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

  readonly headerHeight = 50;
  readonly rowHeight = 50;
  ColumnMode = ColumnMode;
  SelectionType = SelectionType;
  SortType = SortType;
  reorderable = true;
  loading = false;
  mode: string = 'New Responses';

  columns = [
    { prop: "hearing_location", name: "Court Location" },
    { prop: "name", name: "Name" },
    { prop: "ticket_number", name: "Ticket #" },
    { prop: "created_date", name: "Response Date" },
    { prop: "action", name: "Action" }
  ];

  data: SearchResponse = {
    count: 0,
    next: null,
    previous: null,
    results: null
  };
  rows = [];
  selected = [];
  searchParameters: SearchParameters = {
    filterParameters: {
      search: "",
      createdDate: "",
      region: "",
      offset: 0,
      limit: 100 //Hard coded to 100 on the API server for now. 
    },
    sortParameters: [],
  };
  maxSelectedRecords = 50;


  ngOnInit() {
    this.onScroll(0);
  }

  constructor(private adminService: AdminDataService, private el: ElementRef) {
    this.AdminService = adminService;

    //This will disable text highlighting while shift is held down.
    ["keyup", "keydown"].forEach((event) => {
      window.addEventListener(event, (e: KeyboardEvent) => {
        document.onselectstart = function () {
          return !(e.key == "Shift" && e.shiftKey);
        };
      });
    });

    this.searchParameters.sortParameters = [{ prop: 'hearing_location', dir: 'asc' }, {prop: 'created_date', dir: 'asc'}, { prop: 'name', dir: 'asc' }];
  }
  //#endregion Variables & Constructor

  onScroll(offsetY: number) {
    // total height of all rows in the viewport
    const viewHeight = this.el.nativeElement.getBoundingClientRect().height - this.headerHeight;

    // check if we scrolled to the end of the viewport
    if (!this.loading && offsetY + viewHeight >= this.rows.length * this.rowHeight) {
      // total number of results to load
      let limit = this.searchParameters.filterParameters.limit;

      // check if we haven't fetched any results yet
      if (this.rows.length === 0) {
        // calculate the number of rows that fit within viewport
        const pageSize = Math.ceil(viewHeight / this.rowHeight);

        // change the limit to pageSize such that we fill the first page entirely
        // (otherwise, we won't be able to scroll past it)
        limit = Math.max(pageSize, this.searchParameters.filterParameters.limit);
      }
      this.loadPage(limit);
    }
  }

  private async loadPage(limit: number) {
    // set the loading flag, which serves two purposes:
    // 1) it prevents the same page from being loaded twice
    // 2) it enables display of the loading indicator
    this.loading = true;
    this.data = await this.AdminService.getSearchResponse(this.searchParameters);
    this.searchParameters.filterParameters.offset += this.data.results.length;
    const rows = [...this.rows, ...this.data.results];
    this.rows = rows;
    this.loading = false;
  }


  async executeSearch(searchParameters: SearchParameters) {
    this.searchParameters.filterParameters.offset = 0;
    this.loading = true;
    this.data = await this.AdminService.getSearchResponse(this.searchParameters);
    this.loading = false;
    this.rows = this.data.results;
    this.selected = [];
  }

  responseDateText() : string {
    if (this.searchParameters.filterParameters.createdDate == null)
     return 'All Response Dates';
    return `Response Date: ${this.searchParameters.filterParameters.createdDate}`
  }

  filterByRegion(region: string) {
    this.searchParameters.filterParameters.region = region;
    this.executeSearch(this.searchParameters);
  }

  filterByNameOrTicketNumber(search: string) {
    this.searchParameters.filterParameters.search = search;
    this.executeSearch(this.searchParameters);
  }

  filterByResponseDate(responseNgbDate: NgbDateStruct) {
    this.searchParameters.filterParameters.createdDate = new Date(
      responseNgbDate.year,
      responseNgbDate.month - 1,
      responseNgbDate.day
    ).toISOString();
    this.executeSearch(this.searchParameters);
  }

  sort(event) {
    console.log("Sort Event Triggered", event);
    this.loading = true;
    this.searchParameters.sortParameters = event.sorts;
    this.executeSearch(this.searchParameters);
  }

  select({ selected }) {  
    if (selected.length > this.maxSelectedRecords) {
      this.selected = selected.slice(0,this.maxSelectedRecords);
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
