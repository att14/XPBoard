TicketStatusCtrl = ['$scope', function ($scope) {
  $scope.statuses = ["New", "Assigned", "In Review", "Ship-It", "On Prod"]
  $scope.tickets = [
    {
      ticket_id: 34567,
      review_request_id: 56738,
      status: "New"
    },
    {
      ticket_id: 11111,
      review_request_id: 22222,
      status: "In Review"
    },
    {
      ticket_id: 90390,
      review_request_id: 32452,
      status: "Ship-It"
    },
    {
      ticket_id: 34567,
      review_request_id: 56738,
      status: "New"
    },
    {
      ticket_id: 11111,
      review_request_id: 22222,
      status: "In Review"
    },
    {
      ticket_id: 90390,
      review_request_id: 32452,
      status: "Ship-It"
    },
    {
      ticket_id: 11111,
      review_request_id: 22222,
      status: "In Review"
    },
    {
      ticket_id: 90390,
      review_request_id: 32452,
      status: "Ship-It"
    },
    {
      ticket_id: 90390,
      review_request_id: 32452,
      status: "Ship-It"
    },
    {
      ticket_id: 90390,
      review_request_id: 32452,
      status: "Ship-It"
    },
    {
      ticket_id: "awesome",
      review_request_id: "sweet",
      status: "On Prod"
    }
  ]
  $scope.ticketsByStatus = _.groupBy($scope.tickets, 'status')
}];

ReviewStatusCtrl = ['$scope', function ReviewStatusCtrl($scope) {
  
}];

UserStatusCtrl = ['$scope', 'DataFetcher', function UserStatusCtrl($scope, DataFetcher) {
    var dataFetcher = new DataFetcher(function(users) {
        $scope.users = users;
    });
    dataFetcher.userData(['atribone', 'imalison', 'anthony', 'sraveend']);
}]
