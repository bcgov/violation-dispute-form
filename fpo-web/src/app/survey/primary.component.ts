import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { GeneralDataService } from "../general-data.service";
import { MatomoTracker } from "@ambroise-rabier/ngx-matomo";

declare var window: any;

@Component({
  selector: "app-survey-primary",
  templateUrl: "./primary.component.html",
  styleUrls: ["./primary.component.scss"]
})
export class SurveyPrimaryComponent implements OnInit {
  public cacheName: string;
  public printUrl: string;
  public resultJson: any;
  public surveyPath: string;
  public submitted: boolean;
  public emailStatus: boolean;
  public surveyJson: any;
  public complete: Function;
  public data: any;
  public jsonObject: any;
  protected initialMode = "";

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dataService: GeneralDataService,
    private matomoTracker: MatomoTracker
  ) {}

  ngOnInit() {
    const routeData = this.route.snapshot.data;
    this.surveyPath = routeData.survey_path;
    this.surveyJson = routeData.survey;
    this.cacheName = routeData.cache_name;
    this.dataService.emailStatus.subscribe(emailStatus => this.emailStatus = emailStatus)
    const hash = this.route.snapshot.fragment;
    if (hash === "print") this.initialMode = "print";
  }

  onSubmit(submitted: boolean) {
    console.log("Summited the form?", submitted)
    this.submitted = submitted
  }

  showPrintable(data) {
    this.resultJson = JSON.stringify(data);
    this.jsonObject = JSON.parse(this.resultJson);
    console.log("data is =", this.jsonObject)
    //this.printUrl = this.dataService.getApiUrl("form/?name=notice-to-disputant-response");
    
  }

  previewPdf(){
    //We should already have session loaded for this.
    window.open(this.dataService.getApiUrl("pdf/")); 
  }

  onPrint() {
    this.matomoTracker.trackEvent("Survey", "Printed");
 }
}
