import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { GeneralDataService } from "app/general-data.service";
import { Location } from "@angular/common";

@Component({
  selector: "app-contact-component",
  templateUrl: "./contact.component.html",
  styleUrls: ["./contact.component.scss"],
})
export class ContactComponent implements OnInit {
  //#region Variables & Constructor
  public loading = true;
  private _loginRedirect: string = null;

  ngOnInit() {

  }

  constructor(
    private generalDataService: GeneralDataService,
    private route: ActivatedRoute,
    private location: Location
  ) {}
  //#endregion Variables & Constructor

}
