import { Component, OnInit, ElementRef } from "@angular/core";
import { ColumnMode, SelectionType, SortType } from "@swimlane/ngx-datatable";
import { NgbDateStruct } from "@ng-bootstrap/ng-bootstrap";
import { AdminDataService} from './admin-data.service';
import { ActivatedRoute } from '@angular/router';
import { SearchParameters, Region, SearchResponse, RegionCountResponse } from 'app/interfaces/admin_interfaces';

//#region Interfaces
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
  readonly headerHeight = 50;
  loading = false;
  mode: string = 'New Responses';
  selectedRegion: Region =  { name: "All Regions", id: null };
  columns = [];
  regions: Array<Region> = [
    { name: "All Regions", id: null }
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
      isPrinted: false,
      createdDate: "",
      region: null,
      page: 1,
      offset: 0,
      limit: 50 
    },
    sortParameters: [],
  };
  newCountString: string;
  archiveCountString: string;
  maxSelectedRecords = 50;
  totalElements = 0;

  ngOnInit() {
    this.loadPage();
  }

  constructor(private adminService: AdminDataService, private activatedRoute: ActivatedRoute) {
    this.AdminService = adminService;

    this.populateRegions();
    this.buildCountStrings();

    activatedRoute.data.subscribe((data) => {
      if ( data.title === 'New Responses')
        this.switchToNewResponses();
      else 
        this.switchToArchive();
    });

    //This will disable text highlighting while shift is held down.
    ["keyup", "keydown"].forEach((event) => {
      window.addEventListener(event, (e: KeyboardEvent) => {
        document.onselectstart = function () {
          return !(e.key == "Shift" && e.shiftKey);
        };
      });
    });

    this.searchParameters.sortParameters = [{ prop: 'hearing_location__name', dir: 'asc' }, {prop: 'created_date', dir: 'asc'}, { prop: 'name', dir: 'asc' }];
  }
  //#endregion Variables & Constructor


  async populateRegions() {
    if (this.regions.length == 1) {
      var regions = await this.adminService.getRegions() as Array<Region>;
      this.regions = this.regions.concat(regions);
    }
  }

  async buildCountStrings() {
      var counts = await this.adminService.getCounts() as RegionCountResponse;
      this.newCountString = '';
      this.archiveCountString = '';

      this.newCountString += `All Regions: ${counts.new_count.total.count}`;
      counts.new_count.by_region.forEach(element => {
        this.newCountString += ` | ${element.name}: ${element.count}`;
      });
  
      this.archiveCountString += `All Regions: ${counts.archive_count.total.count}`;
      counts.archive_count.by_region.forEach(element => {
        this.archiveCountString += ` | ${element.name}: ${element.count}`;
      });
  }


  switchPage(page: number) {
    this.searchParameters.filterParameters.page = page;
    this.searchParameters.filterParameters.offset = this.searchParameters.filterParameters.limit * (page-1);
    this.loadPage();
  }

  async loadPage() {
    this.selected = [];
    this.loading = true;
    this.data = await this.AdminService.getSearchResponse(this.searchParameters);
    this.loading = false;
    this.totalElements = this.data.count;
    this.rows = this.data.results;
  }

  switchToNewResponses() {
    this.columns = [
      { prop: "hearing_location__name", name: "Court Location" },
      { prop: "name", name: "Name" },
      { prop: "ticket_number", name: "Ticket #" },
      { prop: "created_date", name: "Response Date" },
      { prop: "action", name: "Action" }
    ];

    this.searchParameters.filterParameters.isPrinted = false;
    this.mode = 'New Responses';
  }

  switchToArchive() {
    this.columns = [
      { prop: "hearing_location__name", name: "Court Location" },
      { prop: "name", name: "Name" },
      { prop: "ticket_number", name: "Ticket #" },
      { prop: "created_date", name: "Response Date" },
      { prop: "originally_printed_by", name: "Originally Printed By" },
      { prop: "action", name: "Action"},
    ];

    this.searchParameters.filterParameters.isPrinted = true;
    this.mode = 'Archive'; 
  }

  async executeSearch(searchParameters: SearchParameters) {
    this.searchParameters.filterParameters.offset = 0;
    this.loadPage();
  }

  filterByRegion(region: Region) {
    this.searchParameters.filterParameters.region = region.id;
    this.selectedRegion = region;
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

  totalPages(rowCount: number, pageSize: number) {
    return Math.ceil(rowCount/ pageSize);
  }
}
