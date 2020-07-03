import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { GeneralDataService } from 'app/general-data.service';
import { Injectable } from '@angular/core';

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(public generalDataService: GeneralDataService, public router: Router) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot)  {
        return true;
        if (this.generalDataService.isLoggedIn() && this.generalDataService.isAdmin()) {
          return true;
        }
        //TODO take the user back to the login screen. 
        return this.router.createUrlTree(['/']);
  }
}