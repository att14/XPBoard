var XPBoard = angular.module('XPBoard', []).config(
  ['$routeProvider', '$locationProvider',
   function($routeProvider, $locationProvider) {
     var templateRoot = "/static/js/view_templates/";
     $routeProvider.when("/ticket_status", {
       templateUrl: templateRoot + "ticket_status.html",
       controller: TicketStatusCtrl
     }).when("/review_status",
       {
         templateUrl: templateRoot + "review_status.html",
         controller: ReviewStatusCtrl
       }
     ).otherwise({
       redirectTo: "/ticket_status"
     })
  }]
);
