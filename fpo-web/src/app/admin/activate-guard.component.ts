import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';

export class ActivateGuard implements CanActivate {
    canActivate(
      next: ActivatedRouteSnapshot,
      state: RouterStateSnapshot): boolean {
          //Auth service is logged in.
          //     this.router.navigateByUrl('/notauthorized');

          /*
           if (!this.authService.isLoggedIn) {
      return this.router.createUrlTree(
        ['/notauth', { message: 'you do not have the permission to enter' }]
        // { skipLocationChange: true }
            );
            } else {
            return true;
            }
            */
        return true;
    }
  }