import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
} from "@angular/router";
import { GeneralDataService } from "app/general-data.service";
import { Injectable } from "@angular/core";
import { Location } from "@angular/common";
import { ToastrService } from "ngx-toastr";

@Injectable()
export class AuthGuard implements CanActivate {
  constructor(
    public generalDataService: GeneralDataService,
    public router: Router,
    private location: Location,
    private toastr: ToastrService
  ) {}

  async canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    let routeRequiresSuperUser = route.data.role === "superuser";
    if (
      (routeRequiresSuperUser && this.generalDataService.isSuperUser()) ||
      (!routeRequiresSuperUser && this.generalDataService.isAdmin())
    ) {
      return true;
    }

    try {
      var userInfo = await this.generalDataService.loadUserInfo();
    } catch (error) {
      console.error(error);
      this.toastr.error(this.generalDataService.GenericErrorMessage, "Error");
      return this.router.createUrlTree(["/"]);
    }
    if (!userInfo || !userInfo.user_id) {
      let extUri =
        window.location.origin + this.location.prepareExternalUrl(state.url);
      if (extUri.substr(-1) != "/") extUri += "/";

      let url = new URL(userInfo.login_uri);
      url.searchParams.append("next", extUri);
      window.location.replace(url.toString());
    } else if (
      (routeRequiresSuperUser && userInfo.is_superuser) ||
      (!routeRequiresSuperUser && userInfo.is_staff)
    ) {
      return true;
    } else {
      return this.router.createUrlTree(["/"]);
    }
  }
}
