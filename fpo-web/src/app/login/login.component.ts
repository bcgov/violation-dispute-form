import { Component, OnInit } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { GeneralDataService } from "app/general-data.service";
import { Location } from "@angular/common";

@Component({
  selector: "app-login-component",
  templateUrl: "./login.component.html",
  styleUrls: ["./login.component.scss"],
})
export class LoginComponent implements OnInit {
  //#region Variables & Constructor
  public loading = true;
  private _loginRedirect: string = null;

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      this._loginRedirect = params.next;
      this.loadUserInfo();
    });
  }

  constructor(
    private generalDataService: GeneralDataService,
    private route: ActivatedRoute,
    private router: Router,
    private location: Location
  ) {}
  //#endregion Variables & Constructor

  async loadUserInfo() {
    debugger;
    if (!this._loginRedirect) {
      var userInfo = await this.generalDataService.loadUserInfo();
      this.generalDataService.returnUserInfo(userInfo);
      if (!userInfo.user_id) {
        window.location.replace(userInfo.login_uri);
      }
      else {
        this.router.navigate(['/admin']);
      }
    }
  }
}
