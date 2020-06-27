import { Component, OnInit, ElementRef } from "@angular/core";
import { ColumnMode, SelectionType, SortType } from "@swimlane/ngx-datatable";
import { AdminDataService } from "./admin-data.service";
import { ActivatedRoute } from "@angular/router";
import {
  SearchParameters,
  Region,
  SearchResponse,
  RegionCountResponse,
  AdminPageMode,
} from "app/interfaces/admin_interfaces";

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
  AdminMode = AdminPageMode;
  mode = AdminPageMode.NewResponse;
  selectedRegion: Region = { name: "All Regions", id: null };
  columns = [];
  regions: Array<Region> = [{ name: "All Regions", id: null }];
  data: SearchResponse = {
    count: 0,
    next: null,
    previous: null,
    results: null,
  };
  rows = [];
  selected = [];
  searchParameters: SearchParameters = {
    filterParameters: {
      search: "",
      isArchived: false,
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
  searchCount = 0;
  outdatedBrowser = false;
  closeAlert = false;

  ngOnInit() {
    this.loadPage();
    this.outdatedBrowser = this.checkForIE();
  }

  constructor(
    private adminService: AdminDataService,
    private activatedRoute: ActivatedRoute
  ) {
    this.AdminService = adminService;

    this.populateRegions();
    this.buildCountStrings();

    activatedRoute.data.subscribe((data) => {
      if (data.title === "New Responses") this.switchToNewResponses();
      else this.switchToArchive();
    });

    //This will disable text highlighting while shift is held down.
    ["keyup", "keydown"].forEach((event) => {
      window.addEventListener(event, (e: KeyboardEvent) => {
        document.onselectstart = function () {
          return !(e.key == "Shift" && e.shiftKey);
        };
      });
    });
  }
  //#endregion Variables & Constructor

  async populateRegions() {
    if (this.regions.length == 1) {
      var regions = (await this.adminService.getRegions()) as Array<Region>;
      this.regions = this.regions.concat(regions);
    }
  }

  async buildCountStrings() {
    var counts = (await this.adminService.getCounts()) as RegionCountResponse;
    this.newCountString = "";
    this.archiveCountString = "";

    this.newCountString += `New - All: ${counts.new_count.total.count}`;
    counts.new_count.by_region.forEach((element) => {
      this.newCountString += ` | ${element.name}: ${element.count}`;
    });

    this.archiveCountString += `Archive - All: ${counts.archive_count.total.count}`;
    counts.archive_count.by_region.forEach((element) => {
      this.archiveCountString += ` | ${element.name}: ${element.count}`;
    });
  }

  switchPage(page: number, pagerLocation: string) {
    if (pagerLocation == "bottom") {
      document.getElementById("newResponseTab").scrollIntoView();
    }
    this.searchParameters.filterParameters.page = page;
    this.searchParameters.filterParameters.offset =
      this.searchParameters.filterParameters.limit * (page - 1);
    this.loadPage();
  }

  async loadPage() {
    this.selected = [];
    this.loading = true;
    this.searchCount++;
    let localSearchCount = this.searchCount;
    this.data = await this.AdminService.getSearchResponse(
      this.searchParameters
    );
    this.loading = false;
    //This ensures we only get the latest search.
    if (localSearchCount == this.searchCount) {
      this.totalElements = this.data.count;
      this.rows = this.data.results;
    }
  }

  switchToNewResponses() {
    this.columns = [
      { prop: "hearing_location__name", name: "Court Location" },
      { prop: "name", name: "Name" },
      { prop: "ticket_number", name: "Ticket #" },
      { prop: "created_date", name: "Response Date" },
      { prop: "prepared_pdf", name: "Action" },
    ];
    this.searchParameters.filterParameters.isArchived = false;
    this.searchParameters.sortParameters = [
      { prop: "hearing_location__name", dir: "asc" },
      { prop: "created_date", dir: "asc" },
      { prop: "name", dir: "asc" },
    ];
    this.closeAlert = true;
    this.mode = AdminPageMode.NewResponse
  }

  switchToArchive() {
    this.columns = [
      { prop: "hearing_location__name", name: "Court Location" },
      { prop: "name", name: "Name" },
      { prop: "ticket_number", name: "Ticket #" },
      { prop: "created_date", name: "Response Date" },
      { prop: "archived_by__name", name: "Archived By" },
      { prop: "archived_date", name: "Archived On" },
      { prop: "prepared_pdf", name: "Action" },
    ];
    this.searchParameters.filterParameters.isArchived = true;
    this.searchParameters.sortParameters = [
      { prop: "hearing_location__name", dir: "asc" },
      { prop: "name", dir: "asc" },
      { prop: "ticket_number", dir: "asc" },
    ];
    this.closeAlert = true;
    this.mode = AdminPageMode.Archive;
  }

  async executeSearch(searchParameters: SearchParameters) {
    if (
      searchParameters.filterParameters.search.length < 3 &&
      searchParameters.filterParameters.search.length > 0
    )
      return;
    this.searchParameters.filterParameters.offset = 0;
    this.loadPage();
  }

  filterByRegion(region: Region) {
    this.searchParameters.filterParameters.region = region.id;
    this.selectedRegion = region;
    this.executeSearch(this.searchParameters);
  }

  search(search: string) {
    this.searchParameters.filterParameters.search = search;
    this.executeSearch(this.searchParameters);
  }

  sort(event) {
    this.searchParameters.sortParameters = event.sorts;
    this.executeSearch(this.searchParameters);
  }

  select({ selected }) {
    if (selected.length > this.maxSelectedRecords) {
      this.selected = selected.slice(0, this.maxSelectedRecords);
      return;
    }
    this.selected.splice(0, this.selected.length);
    this.selected.push(...selected);
  }

  printSelected() {
    this.print([
      ...this.selected.map((ticketResponse) => ticketResponse.prepared_pdf),
    ]);
  }

  printTop50() {
    this.print([
      ...this.rows.map((ticketResponse) => ticketResponse.prepared_pdf),
    ]);
  }

  //TODO currently doesn't work with IE.
  async print(targetIds: Array<number>) {
    var response = await this.adminService.getPdf(targetIds);
    var file = new Blob([response], { type: "application/pdf" });
    var fileURL = URL.createObjectURL(file);
    var oWindow = window.open(fileURL);
    let popupBlocked = false;
    try {
      //Check for popup blocker.
      oWindow.print();
    } catch {
      popupBlocked = true;
    }
    window.URL.revokeObjectURL(fileURL);
    if (!popupBlocked) {
      //If successful, hit the API again and mark files as printed.
      if (this.mode === AdminPageMode.NewResponse) {
        await this.adminService.markFilesAsArchived(targetIds);
      }

      window.onfocus = () => {
        //Fix tooltip from remaining open. 
        if (document.activeElement instanceof HTMLElement)
        document.activeElement.blur();
        this.closeAlert = false;
        setTimeout(() => (this.closeAlert = true), 5000);
        window.onfocus = null;
      }

      //This resets us to the first page.
      this.executeSearch(this.searchParameters);
    }
  }

  openPdf(event: MouseEvent, id: number) {
    event.preventDefault();
    event.stopPropagation();
    window.open(`api/v1/pdf/${id}`);
  }

  totalPages(rowCount: number, pageSize: number) {
    return Math.ceil(rowCount / pageSize);
  }

  checkForIE() {
    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");
    return msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./);
  }
}
