import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { GeneralDataService } from 'app/general-data.service';
import { Injectable } from '@angular/core';

@Injectable()
export class AuthGuard implements CanActivate {

  constructor(public generalDataService: GeneralDataService, public router: Router) { }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot)  {
        if (this.generalDataService.isLoggedIn() && this.generalDataService.isAdmin()) {
          return true;
        }
        return this.router.createUrlTree(['/login']);
  }
}