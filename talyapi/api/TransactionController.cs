using Microsoft.AspNetCore.Mvc;
namespace TaliAPI.Transactions.API
{
    [ApiController]
    [Route("api/[controller]")]
    public class TransactionController : ControllerBase
    {
        private readonly ILogger<TransactionController> _logger;

        public TransactionController(ILogger<TransactionController> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public List<Transaction> Get()
        {
            return new List<Transaction>
            {
                new Transaction { TransactionNumber = "TXN001", Amount = 100.00m, Date = DateTime.Now, Description = "Transaction 1" },
                new Transaction { TransactionNumber = "TXN002", Amount = 200.00m, Date = DateTime.Now, Description = "Transaction 2" }
            };
        }
         [HttpPost("PosTransaction")]
        public List<Transaction> PosTransaction(TransactionRequest request)
        {
            return new List<Transaction>
            {
                new Transaction { TransactionNumber = "TXN001", Amount = 100.00m, Date = DateTime.Now, Description = "Transaction 1" },
                new Transaction { TransactionNumber = "TXN002", Amount = 200.00m, Date = DateTime.Now, Description = "Transaction 2" }
                ,  new Transaction { TransactionNumber = "TXN003", Amount = 200.00m, Date = DateTime.Now, Description = "Transaction 3" }
            };
        }
    }
    public class Transaction
    {
        public string TransactionNumber { get; set; }
        public decimal Amount { get; set; }
        public DateTime Date { get; set; }
        public string Description { get; set; }
    } 
    public class TransactionRequest
    {
        public string TransactionNumber { get; set; }
     
    } 
    
    
}