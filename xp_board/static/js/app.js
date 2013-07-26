var XPBoard = angular.module('XPBoard', []).config(
  ['$routeProvider', '$locationProvider',
   function($routeProvider, $locationProvider) {
     var templateRoot = "/static/js/view_templates/";
     $routeProvider.when("/ticket_status", {
       templateUrl: templateRoot + "ticket_status.html",
       controller: TicketsByStatusCtrl
     }).when("/review_status", {
       templateUrl: templateRoot + "review_status.html",
       controller: ReviewsByUserCtrl
     }).when("/user_status", {
       templateUrl: templateRoot + "user_status.html",
       controller: UserStatusCtrl
     }).otherwise({
       redirectTo: "/by_owner"
     })
  }]
);
