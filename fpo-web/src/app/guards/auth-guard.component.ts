import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
} from "@angular/router";
import { GeneralDataService } from "app/general-data.service";
import { Injectable } from "@angular/core";
import { Location } from "@angular/common";

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(
    public generalDataService: GeneralDataService,
    public router: Router,
    private location: Location
  ) {}

  async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    //Check if we're already logged in.
    if (
      this.generalDataService.isLoggedIn() &&
      this.generalDataService.isAdmin()
    ) {
      return true;
    }

    var userInfo = await this.generalDataService.loadUserInfo();
    if (!userInfo || !userInfo.user_id) {
      const extUri =
        window.location.origin + this.location.prepareExternalUrl("/admin");
      window.location.replace(
        userInfo.login_uri + "?next=" + encodeURIComponent(extUri)
      );
    } else {
      return true;
    }
  }
}
